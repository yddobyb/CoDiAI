import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
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
      final recService = ref.read(recommendationServiceProvider);
      final results = recService.recommend(item);
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
    } catch (e) {
      state = RecommendationState(
        isLoading: false,
        error: 'Failed to generate recommendations',
      );
    }
  }
}

final recommendationProvider =
    NotifierProvider<RecommendationNotifier, RecommendationState>(
  RecommendationNotifier.new,
);
