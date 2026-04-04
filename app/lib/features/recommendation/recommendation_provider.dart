import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../../models/clothing_item.dart';
import '../../models/outfit_recommendation.dart';
import '../../providers/service_providers.dart';

class RecommendationState {
  final List<OutfitRecommendation> recommendations;
  final bool isLoading;
  final bool llmLoading;
  final String? error;

  const RecommendationState({
    this.recommendations = const [],
    this.isLoading = true,
    this.llmLoading = false,
    this.error,
  });

  RecommendationState copyWith({
    List<OutfitRecommendation>? recommendations,
    bool? isLoading,
    bool? llmLoading,
    String? error,
  }) {
    return RecommendationState(
      recommendations: recommendations ?? this.recommendations,
      isLoading: isLoading ?? this.isLoading,
      llmLoading: llmLoading ?? this.llmLoading,
      error: error,
    );
  }
}

class RecommendationNotifier extends Notifier<RecommendationState> {
  @override
  RecommendationState build() => const RecommendationState();

  Future<void> generate(ClothingItem item) async {
    state = const RecommendationState(isLoading: true);

    try {
      // Get user's style preference if logged in
      String? preferredStyle;
      try {
        final user = Supabase.instance.client.auth.currentUser;
        if (user != null) {
          final profile = await Supabase.instance.client
              .from('profiles')
              .select('style_preference')
              .eq('id', user.id)
              .single();
          preferredStyle = profile['style_preference'] as String?;
        }
      } catch (_) {}

      final recService = ref.read(recommendationServiceProvider);
      final results = recService.recommend(item, preferredStyle: preferredStyle);
      state = RecommendationState(
        recommendations: results,
        isLoading: false,
        llmLoading: true,
      );

      final llm = ref.read(llmServiceProvider);
      if (llm.isAvailable) {
        try {
          await llm.generateAll(results);
        } catch (e) {
          debugPrint('[Recommendation] LLM generation failed: $e');
        }
        state = state.copyWith(
          recommendations: List.from(results),
          llmLoading: false,
        );
      } else {
        state = state.copyWith(llmLoading: false);
      }

      // Auto-save to history if logged in
      _saveToHistory(item, results);
    } catch (e) {
      state = RecommendationState(
        isLoading: false,
        error: 'Failed to generate recommendations',
      );
    }
  }

  Future<void> _saveToHistory(ClothingItem item, List<OutfitRecommendation> recs) async {
    try {
      final user = Supabase.instance.client.auth.currentUser;
      if (user == null) {
        debugPrint('[History] Skipped — not logged in');
        return;
      }
      debugPrint('[History] Saving ${recs.length} recommendations...');
      final historyService = ref.read(historyServiceProvider);
      await historyService.saveHistory(userItem: item, recommendations: recs);
      debugPrint('[History] Save success');
    } catch (e) {
      debugPrint('[History] Save failed: $e');
    }
  }
}

final recommendationProvider =
    NotifierProvider<RecommendationNotifier, RecommendationState>(
  RecommendationNotifier.new,
);
