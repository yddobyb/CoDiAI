import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../models/outfit_recommendation.dart';
import '../../providers/service_providers.dart';
import '../../services/daily_outfit_service.dart';

class DailyOutfitState {
  final OutfitRecommendation? outfit;
  final bool isLoading;
  final bool loaded;

  const DailyOutfitState({
    this.outfit,
    this.isLoading = false,
    this.loaded = false,
  });
}

class DailyOutfitNotifier extends Notifier<DailyOutfitState> {
  @override
  DailyOutfitState build() => const DailyOutfitState();

  Future<void> load() async {
    if (state.loaded) return; // Only load once per session

    // Check auth state from provider (safe for tests)
    final authState = ref.read(authStateProvider);
    if (authState.value?.session == null) return;

    state = const DailyOutfitState(isLoading: true);

    try {
      final closetService = ref.read(closetServiceProvider);
      final profileService = ref.read(profileServiceProvider);

      final results = await Future.wait<Object>([
        closetService.fetchItems(),
        profileService.fetchProfile(),
      ]);

      final items = results[0] as List<Map<String, dynamic>>;
      final profile = results[1] as Map<String, dynamic>;

      if (items.isEmpty) {
        state = const DailyOutfitState(loaded: true);
        return;
      }

      final service = DailyOutfitService();
      final outfit = await service.generateDailyOutfit(
        closetItems: items,
        preferredStyle: profile['style_preference'] as String?,
      );

      state = DailyOutfitState(outfit: outfit, loaded: true);
    } catch (e) {
      debugPrint('[DailyOutfit] Error: $e');
      state = const DailyOutfitState(loaded: true);
    }
  }
}

final dailyOutfitProvider =
    NotifierProvider<DailyOutfitNotifier, DailyOutfitState>(
  DailyOutfitNotifier.new,
);
