import 'dart:ui';
import 'package:flutter_test/flutter_test.dart';
import 'package:fashion_codi/models/clothing_item.dart';

void main() {
  group('ClothingItem', () {
    group('slot', () {
      test('top categories return "top"', () {
        for (final cat in ['T-shirt', 'Shirt', 'Hoodie']) {
          final item = ClothingItem(category: cat, color: 'black', style: 'casual');
          expect(item.slot, 'top', reason: '$cat should be top');
        }
      });

      test('Jacket returns "outer"', () {
        final item = ClothingItem(category: 'Jacket', color: 'black', style: 'formal');
        expect(item.slot, 'outer');
      });

      test('bottom categories return "bottom"', () {
        for (final cat in ['Pants', 'Jeans', 'Dress']) {
          final item = ClothingItem(category: cat, color: 'blue', style: 'casual');
          expect(item.slot, 'bottom', reason: '$cat should be bottom');
        }
      });

      test('shoes categories return "shoes"', () {
        for (final cat in ['Sneakers', 'Boots']) {
          final item = ClothingItem(category: cat, color: 'white', style: 'sporty');
          expect(item.slot, 'shoes', reason: '$cat should be shoes');
        }
      });

      test('unknown category defaults to "top"', () {
        final item = ClothingItem(category: 'Hat', color: 'black', style: 'casual');
        expect(item.slot, 'top');
      });
    });

    group('isDress', () {
      test('returns true for Dress', () {
        final item = ClothingItem(category: 'Dress', color: 'red', style: 'formal');
        expect(item.isDress, isTrue);
      });

      test('returns false for non-Dress', () {
        final item = ClothingItem(category: 'Jeans', color: 'blue', style: 'casual');
        expect(item.isDress, isFalse);
      });
    });

    group('icon', () {
      test('returns correct emoji for each category', () {
        expect(ClothingItem(category: 'T-shirt', color: 'w', style: 's').icon, '👕');
        expect(ClothingItem(category: 'Shirt', color: 'w', style: 's').icon, '👔');
        expect(ClothingItem(category: 'Dress', color: 'w', style: 's').icon, '👗');
        expect(ClothingItem(category: 'Jeans', color: 'w', style: 's').icon, '👖');
        expect(ClothingItem(category: 'Sneakers', color: 'w', style: 's').icon, '👟');
        expect(ClothingItem(category: 'Boots', color: 'w', style: 's').icon, '🥾');
      });

      test('unknown category defaults to shirt emoji', () {
        final item = ClothingItem(category: 'Unknown', color: 'w', style: 's');
        expect(item.icon, '👕');
      });
    });

    group('colorValue', () {
      test('returns non-null color for all known colors', () {
        for (final color in ClothingItem.allColors) {
          final item = ClothingItem(category: 'T-shirt', color: color, style: 'casual');
          expect(item.colorValue, isNotNull, reason: '$color should have a color value');
        }
      });

      test('unknown color defaults to gray', () {
        final item = ClothingItem(category: 'T-shirt', color: 'purple', style: 'casual');
        // Gray = Color(0xFF808080)
        expect(item.colorValue, const Color(0xFF808080));
      });
    });

    group('static lists', () {
      test('allCategories contains 9 items', () {
        expect(ClothingItem.allCategories.length, 9);
      });

      test('allColors contains 7 colors', () {
        expect(ClothingItem.allColors.length, 7);
      });

      test('category lists cover all categories', () {
        final covered = {
          ...ClothingItem.topCategories,
          ...ClothingItem.outerCategories,
          ...ClothingItem.bottomCategories,
          ...ClothingItem.shoesCategories,
        };
        expect(covered, containsAll(ClothingItem.allCategories));
      });
    });

    group('confidence default', () {
      test('defaults to 0.0', () {
        final item = ClothingItem(category: 'T-shirt', color: 'black', style: 'casual');
        expect(item.confidence, 0.0);
      });

      test('can be set', () {
        final item = ClothingItem(
          category: 'T-shirt', color: 'black', style: 'casual', confidence: 0.95,
        );
        expect(item.confidence, 0.95);
      });
    });
  });
}
