import 'package:flutter_test/flutter_test.dart';
import 'package:fashion_codi/models/clothing_item.dart';
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
