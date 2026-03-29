import 'package:flutter_test/flutter_test.dart';
import 'package:fashion_codi/features/recommendation/recommendation_provider.dart';

void main() {
  group('RecommendationState', () {
    test('default state is loading with empty recommendations', () {
      const state = RecommendationState();
      expect(state.isLoading, isTrue);
      expect(state.llmLoading, isFalse);
      expect(state.recommendations, isEmpty);
      expect(state.error, isNull);
    });

    test('copyWith preserves unchanged fields', () {
      const state = RecommendationState(isLoading: false, llmLoading: true);
      final copied = state.copyWith(llmLoading: false);
      expect(copied.isLoading, isFalse);
      expect(copied.llmLoading, isFalse);
      expect(copied.recommendations, isEmpty);
    });

    test('copyWith can set error', () {
      const state = RecommendationState();
      final copied = state.copyWith(error: 'Something failed');
      expect(copied.error, 'Something failed');
    });
  });
}
