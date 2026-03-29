import 'package:flutter_test/flutter_test.dart';
import 'package:fashion_codi/models/clothing_item.dart';
import 'package:fashion_codi/models/outfit_recommendation.dart';

void main() {
  group('OutfitRecommendation', () {
    late ClothingItem userItem;
    late List<ClothingItem> recItems;

    setUp(() {
      userItem = const ClothingItem(
        category: 'T-shirt', color: 'blue', style: 'casual',
        confidence: 0.95, imagePath: '/test.jpg',
      );
      recItems = const [
        ClothingItem(category: 'Jeans', color: 'black', style: 'casual'),
        ClothingItem(category: 'Sneakers', color: 'white', style: 'sporty'),
      ];
    });

    test('allItems includes user item first', () {
      final rec = OutfitRecommendation(
        userItem: userItem,
        recommendedItems: recItems,
        matchScore: 0.85,
        categoryScore: 0.9,
        colorScore: 0.8,
        styleScore: 0.7,
        matchReason: 'test',
        colorHarmony: 'test',
        styleConsistency: 'test',
      );
      expect(rec.allItems.length, 3);
      expect(rec.allItems.first, userItem);
    });

    test('matchPercent rounds correctly', () {
      final rec = OutfitRecommendation(
        userItem: userItem,
        recommendedItems: recItems,
        matchScore: 0.856,
        categoryScore: 0.9,
        colorScore: 0.8,
        styleScore: 0.7,
        matchReason: 'test',
        colorHarmony: 'test',
        styleConsistency: 'test',
      );
      expect(rec.matchPercent, 86);
    });

    test('llmDescription is nullable and mutable', () {
      final rec = OutfitRecommendation(
        userItem: userItem,
        recommendedItems: recItems,
        matchScore: 0.85,
        categoryScore: 0.9,
        colorScore: 0.8,
        styleScore: 0.7,
        matchReason: 'test',
        colorHarmony: 'test',
        styleConsistency: 'test',
      );
      expect(rec.llmDescription, isNull);

      rec.llmDescription = 'AI generated tip';
      expect(rec.llmDescription, 'AI generated tip');
    });
  });
}
