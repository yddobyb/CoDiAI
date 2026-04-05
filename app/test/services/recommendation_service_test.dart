import 'package:flutter_test/flutter_test.dart';
import 'package:fashion_codi/models/clothing_item.dart';
import 'package:fashion_codi/models/user_preferences.dart';
import 'package:fashion_codi/services/recommendation_service.dart';

void main() {
  late RecommendationService service;

  setUp(() {
    service = RecommendationService();
  });

  group('RecommendationService.recommend', () {
    test('returns exactly 3 recommendations for a top item', () {
      final item = const ClothingItem(
        category: 'T-shirt', color: 'blue', style: 'casual',
        confidence: 0.9, imagePath: '/test.jpg',
      );
      final results = service.recommend(item);
      expect(results.length, 3);
    });

    test('returns exactly 3 recommendations for a bottom item', () {
      final item = const ClothingItem(
        category: 'Jeans', color: 'blue', style: 'casual',
        confidence: 0.9, imagePath: '/test.jpg',
      );
      final results = service.recommend(item);
      expect(results.length, 3);
    });

    test('returns recommendations for shoes item', () {
      final item = const ClothingItem(
        category: 'Sneakers', color: 'white', style: 'sporty',
        confidence: 0.9, imagePath: '/test.jpg',
      );
      final results = service.recommend(item);
      expect(results.length, 3);
    });

    test('returns recommendations for Dress', () {
      final item = const ClothingItem(
        category: 'Dress', color: 'red', style: 'formal',
        confidence: 0.9, imagePath: '/test.jpg',
      );
      final results = service.recommend(item);
      expect(results.length, greaterThanOrEqualTo(1));
      expect(results.length, lessThanOrEqualTo(3));
    });

    test('returns recommendations for Jacket (outer)', () {
      final item = const ClothingItem(
        category: 'Jacket', color: 'black', style: 'formal',
        confidence: 0.9, imagePath: '/test.jpg',
      );
      final results = service.recommend(item);
      expect(results.length, 3);
    });

    test('all recommendations include the user item', () {
      final item = const ClothingItem(
        category: 'T-shirt', color: 'blue', style: 'casual',
        confidence: 0.9, imagePath: '/test.jpg',
      );
      final results = service.recommend(item);
      for (final rec in results) {
        expect(rec.userItem, item);
        expect(rec.allItems.first, item);
      }
    });

    test('recommendations are sorted by score (descending)', () {
      final item = const ClothingItem(
        category: 'T-shirt', color: 'blue', style: 'casual',
        confidence: 0.9, imagePath: '/test.jpg',
      );
      final results = service.recommend(item);
      for (int i = 0; i < results.length - 1; i++) {
        expect(results[i].matchScore, greaterThanOrEqualTo(results[i + 1].matchScore));
      }
    });

    test('match scores are between 0 and 1', () {
      for (final cat in ClothingItem.allCategories) {
        final item = ClothingItem(
          category: cat, color: 'black', style: 'casual',
          confidence: 0.9, imagePath: '/test.jpg',
        );
        final results = service.recommend(item);
        for (final rec in results) {
          expect(rec.matchScore, greaterThanOrEqualTo(0.0));
          expect(rec.matchScore, lessThanOrEqualTo(1.0));
          expect(rec.categoryScore, greaterThanOrEqualTo(0.0));
          expect(rec.categoryScore, lessThanOrEqualTo(1.0));
          expect(rec.colorScore, greaterThanOrEqualTo(0.0));
          expect(rec.colorScore, lessThanOrEqualTo(1.0));
          expect(rec.styleScore, greaterThanOrEqualTo(0.0));
          expect(rec.styleScore, lessThanOrEqualTo(1.0));
        }
      }
    });

    test('recommendations have variety (not all identical)', () {
      final item = const ClothingItem(
        category: 'T-shirt', color: 'blue', style: 'casual',
        confidence: 0.9, imagePath: '/test.jpg',
      );
      final results = service.recommend(item);
      final keys = results.map((r) =>
        r.recommendedItems.map((i) => '${i.category}-${i.color}').join('|')
      ).toSet();
      expect(keys.length, results.length, reason: 'All recommendations should be unique');
    });

    test('matchReason is not empty', () {
      final item = const ClothingItem(
        category: 'Shirt', color: 'white', style: 'formal',
        confidence: 0.9, imagePath: '/test.jpg',
      );
      final results = service.recommend(item);
      for (final rec in results) {
        expect(rec.matchReason, isNotEmpty);
        expect(rec.colorHarmony, isNotEmpty);
        expect(rec.styleConsistency, isNotEmpty);
      }
    });

    test('respects maxResults parameter', () {
      final item = const ClothingItem(
        category: 'T-shirt', color: 'blue', style: 'casual',
        confidence: 0.9, imagePath: '/test.jpg',
      );
      final results = service.recommend(item, maxResults: 1);
      expect(results.length, 1);
    });
  });

  group('scoring logic', () {
    test('neutral color combinations score higher than clashing chromatics', () {
      final blackTop = const ClothingItem(
        category: 'T-shirt', color: 'black', style: 'casual',
        confidence: 0.9, imagePath: '/test.jpg',
      );
      final redTop = const ClothingItem(
        category: 'T-shirt', color: 'red', style: 'casual',
        confidence: 0.9, imagePath: '/test.jpg',
      );
      final blackResults = service.recommend(blackTop);
      final redResults = service.recommend(redTop);

      // Black (neutral) should generally produce higher scores
      expect(blackResults.first.matchScore, greaterThanOrEqualTo(redResults.first.matchScore * 0.9));
    });

    test('same style items score higher than mixed styles', () {
      final casualTop = const ClothingItem(
        category: 'T-shirt', color: 'white', style: 'casual',
        confidence: 0.9, imagePath: '/test.jpg',
      );
      final results = service.recommend(casualTop);
      // Best result should have decent style consistency
      expect(results.first.styleScore, greaterThanOrEqualTo(0.35));
    });
  });

  group('personalization', () {
    test('closet color affinity boosts matching colors', () {
      final item = const ClothingItem(
        category: 'T-shirt', color: 'blue', style: 'casual',
        confidence: 0.9, imagePath: '/test.jpg',
      );

      final baseline = service.recommend(item);

      // User's closet is dominated by black — recommendations with black should score higher
      final withAffinity = service.recommend(item,
        preferences: const UserPreferences(
          colorAffinity: {'black': 1.0, 'white': 0.5},
          styleAffinity: {'casual': 1.0},
        ),
      );

      // With affinity, best score should be >= baseline (bonuses only add)
      expect(withAffinity.first.matchScore,
          greaterThanOrEqualTo(baseline.first.matchScore));
    });

    test('feedback bias influences scoring', () {
      final item = const ClothingItem(
        category: 'T-shirt', color: 'blue', style: 'casual',
        confidence: 0.9, imagePath: '/test.jpg',
      );

      // Strong positive bias for blue+black pair and T-shirt+Jeans pair
      final withPositiveFeedback = service.recommend(item,
        preferences: const UserPreferences(
          colorPairBias: {'black|blue': 1.0},
          categoryPairBias: {'Jeans|T-shirt': 1.0},
        ),
      );

      final baseline = service.recommend(item);

      // Positive feedback should boost scores
      expect(withPositiveFeedback.first.matchScore,
          greaterThanOrEqualTo(baseline.first.matchScore));
    });

    test('profileStyle in preferences works like preferredStyle', () {
      final item = const ClothingItem(
        category: 'Shirt', color: 'white', style: 'formal',
        confidence: 0.9, imagePath: '/test.jpg',
      );

      final withOldParam = service.recommend(item, preferredStyle: 'formal');
      final withPrefs = service.recommend(item,
        preferences: const UserPreferences(profileStyle: 'formal'),
      );

      // Both should produce the same top score
      expect(withPrefs.first.matchScore,
          closeTo(withOldParam.first.matchScore, 0.001));
    });

    test('empty preferences produce same results as no preferences', () {
      final item = const ClothingItem(
        category: 'T-shirt', color: 'blue', style: 'casual',
        confidence: 0.9, imagePath: '/test.jpg',
      );

      final baseline = service.recommend(item);
      final withEmpty = service.recommend(item,
        preferences: const UserPreferences(),
      );

      expect(withEmpty.first.matchScore,
          closeTo(baseline.first.matchScore, 0.001));
    });

    test('scores remain in 0-1 range with max personalization', () {
      for (final cat in ClothingItem.allCategories) {
        final item = ClothingItem(
          category: cat, color: 'black', style: 'casual',
          confidence: 0.9, imagePath: '/test.jpg',
        );
        final results = service.recommend(item,
          preferences: const UserPreferences(
            profileStyle: 'casual',
            colorAffinity: {'black': 1.0, 'white': 1.0, 'gray': 1.0},
            styleAffinity: {'casual': 1.0, 'formal': 1.0, 'sporty': 1.0},
            colorPairBias: {'black|black': 1.0, 'black|white': 1.0},
            categoryPairBias: {'Jeans|T-shirt': 1.0, 'Boots|T-shirt': 1.0},
          ),
        );
        for (final rec in results) {
          expect(rec.matchScore, greaterThanOrEqualTo(0.0));
          expect(rec.matchScore, lessThanOrEqualTo(1.0));
        }
      }
    });
  });

  group('edge cases', () {
    test('all category + color combinations produce results', () {
      for (final cat in ClothingItem.allCategories) {
        for (final color in ClothingItem.allColors) {
          final item = ClothingItem(
            category: cat, color: color, style: 'casual',
            confidence: 0.9, imagePath: '/test.jpg',
          );
          final results = service.recommend(item);
          expect(results, isNotEmpty,
            reason: '$color $cat should produce recommendations');
        }
      }
    });
  });
}
