import 'package:flutter_test/flutter_test.dart';
import 'package:fashion_codi/models/product.dart';

void main() {
  group('Product', () {
    final sampleMap = {
      'id': 'abc-123',
      'name': 'Essential Crewneck Tee',
      'brand': 'KOTN',
      'category': 'T-shirt',
      'color': 'white',
      'style': 'casual',
      'price': 45,
      'image_url': 'https://example.com/img.jpg',
      'affiliate_url': 'https://example.com/buy',
      'created_at': '2026-04-04T12:00:00Z',
    };

    test('fromMap parses all fields correctly', () {
      final product = Product.fromMap(sampleMap);
      expect(product.id, 'abc-123');
      expect(product.name, 'Essential Crewneck Tee');
      expect(product.brand, 'KOTN');
      expect(product.category, 'T-shirt');
      expect(product.color, 'white');
      expect(product.style, 'casual');
      expect(product.price, 45);
      expect(product.imageUrl, 'https://example.com/img.jpg');
      expect(product.affiliateUrl, 'https://example.com/buy');
    });

    test('fromMap handles null affiliate_url', () {
      final map = Map<String, dynamic>.from(sampleMap)..['affiliate_url'] = null;
      final product = Product.fromMap(map);
      expect(product.affiliateUrl, isNull);
    });

    test('formattedPrice formats CAD correctly', () {
      final product = Product.fromMap(sampleMap);
      expect(product.formattedPrice, '\$45');

      final expensive = Product.fromMap(
        Map<String, dynamic>.from(sampleMap)..['price'] = 298,
      );
      expect(expensive.formattedPrice, '\$298');
    });

    test('slot maps categories correctly', () {
      const cases = {
        'T-shirt': 'top', 'Shirt': 'top', 'Hoodie': 'top', 'Sweater': 'top',
        'Jacket': 'outer', 'Coat': 'outer',
        'Pants': 'bottom', 'Jeans': 'bottom', 'Shorts': 'bottom',
        'Skirt': 'bottom', 'Dress': 'bottom',
        'Sneakers': 'shoes', 'Boots': 'shoes', 'Flats': 'shoes', 'Heels': 'shoes',
      };
      for (final entry in cases.entries) {
        final product = Product.fromMap(
          Map<String, dynamic>.from(sampleMap)..['category'] = entry.key,
        );
        expect(product.slot, entry.value, reason: '${entry.key} → ${entry.value}');
      }
    });

    test('slotLabel returns human readable label', () {
      final product = Product.fromMap(sampleMap);
      expect(product.slotLabel, 'Tops');

      final shoes = Product.fromMap(
        Map<String, dynamic>.from(sampleMap)..['category'] = 'Sneakers',
      );
      expect(shoes.slotLabel, 'Shoes');
    });
  });
}
