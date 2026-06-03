import 'package:flutter_test/flutter_test.dart';
import 'package:fashion_codi/models/clothing_item.dart';
import 'package:fashion_codi/services/search_query_service.dart';

void main() {
  late SearchQueryService service;

  setUp(() {
    service = SearchQueryService();
  });

  group('buildQuery', () {
    test('composes color + category + women + style + season', () {
      const item = ClothingItem(
        category: 'Hoodie',
        color: 'beige',
        style: 'casual',
        season: 'fall',
      );
      expect(service.buildQuery(item), 'beige hoodie women casual fall');
    });

    test('lowercases the category', () {
      const item = ClothingItem(category: 'Sneakers', color: 'white', style: 'sporty');
      expect(service.buildQuery(item), startsWith('white sneakers women'));
    });

    test('omits season when null', () {
      const item = ClothingItem(category: 'Jeans', color: 'blue', style: 'casual');
      expect(service.buildQuery(item), 'blue jeans women casual');
    });

    test('omits season when empty string', () {
      const item = ClothingItem(category: 'Coat', color: 'black', style: 'formal', season: '');
      expect(service.buildQuery(item), 'black coat women formal');
    });

    test('omits style when empty', () {
      const item = ClothingItem(category: 'Shirt', color: 'navy', style: '');
      expect(service.buildQuery(item), 'navy shirt women');
    });

    test('drops empty color without leaving a leading space', () {
      const item = ClothingItem(category: 'Dress', color: '', style: 'formal');
      expect(service.buildQuery(item), 'dress women formal');
    });
  });

  group('buildShopUrls', () {
    test('returns the four Canada-relevant providers in order', () {
      final urls = service.buildShopUrls('beige hoodie women');
      expect(urls.keys.toList(),
          ['Google Shopping', 'Amazon', 'Aritzia', 'SSENSE']);
    });

    test('uses Canadian Amazon and SSENSE storefronts', () {
      final urls = service.buildShopUrls('beige hoodie');
      expect(urls['Amazon']!.host, 'www.amazon.ca');
      expect(urls['SSENSE']!.toString(), contains('/en-ca/'));
    });

    test('url-encodes the query (spaces do not break the URL)', () {
      final urls = service.buildShopUrls('beige hoodie women casual');
      final google = urls['Google Shopping']!.toString();
      // encodeQueryComponent encodes spaces as '+' (query-component standard).
      expect(google, contains('beige+hoodie+women+casual'));
      expect(google, isNot(contains(' ')));
    });

    test('encoded query round-trips back to the original text', () {
      final urls = service.buildShopUrls('navy a-line skirt');
      expect(urls['Amazon']!.queryParameters['k'], 'navy a-line skirt');
    });
  });
}
