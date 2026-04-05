import 'package:flutter_test/flutter_test.dart';
import 'package:fashion_codi/services/personalization_service.dart';

void main() {
  late PersonalizationService service;

  setUp(() {
    service = PersonalizationService();
  });

  group('buildPreferences', () {
    test('returns empty preferences for empty data', () {
      final prefs = service.buildPreferences(
        closetItems: [],
        historyRows: [],
      );
      expect(prefs.colorAffinity, isEmpty);
      expect(prefs.styleAffinity, isEmpty);
      expect(prefs.colorPairBias, isEmpty);
      expect(prefs.categoryPairBias, isEmpty);
      expect(prefs.profileStyle, isNull);
      expect(prefs.hasClosetData, false);
      expect(prefs.hasFeedback, false);
    });

    test('passes through profileStyle', () {
      final prefs = service.buildPreferences(
        closetItems: [],
        historyRows: [],
        profileStyle: 'casual',
      );
      expect(prefs.profileStyle, 'casual');
    });
  });

  group('color affinity from closet', () {
    test('normalizes color frequency to 0-1', () {
      final prefs = service.buildPreferences(
        closetItems: [
          {'color': 'black', 'style': 'casual'},
          {'color': 'black', 'style': 'casual'},
          {'color': 'black', 'style': 'casual'},
          {'color': 'navy', 'style': 'formal'},
          {'color': 'white', 'style': 'casual'},
        ],
        historyRows: [],
      );
      expect(prefs.colorAffinity['black'], 1.0); // 3/3 = most frequent
      expect(prefs.colorAffinity['navy'], closeTo(1 / 3, 0.01));
      expect(prefs.colorAffinity['white'], closeTo(1 / 3, 0.01));
      expect(prefs.hasClosetData, true);
    });

    test('handles single item closet', () {
      final prefs = service.buildPreferences(
        closetItems: [{'color': 'red', 'style': 'casual'}],
        historyRows: [],
      );
      expect(prefs.colorAffinity['red'], 1.0);
    });
  });

  group('style affinity from closet', () {
    test('normalizes style frequency to 0-1', () {
      final prefs = service.buildPreferences(
        closetItems: [
          {'color': 'black', 'style': 'casual'},
          {'color': 'blue', 'style': 'casual'},
          {'color': 'white', 'style': 'formal'},
        ],
        historyRows: [],
      );
      expect(prefs.styleAffinity['casual'], 1.0); // 2/2 = most frequent
      expect(prefs.styleAffinity['formal'], 0.5); // 1/2
    });
  });

  group('feedback bias from history', () {
    test('liked history creates positive bias', () {
      final prefs = service.buildPreferences(
        closetItems: [],
        historyRows: [
          _historyRow(
            liked: true,
            userColor: 'blue',
            userCategory: 'T-shirt',
            recItems: [
              {'category': 'Jeans', 'color': 'black', 'style': 'casual'},
            ],
          ),
        ],
      );
      // Sorted pair: "black|blue"
      expect(prefs.colorPairBias['black|blue'], closeTo(0.1, 0.001));
      // Sorted pair: "Jeans|T-shirt"
      expect(prefs.categoryPairBias['Jeans|T-shirt'], closeTo(0.1, 0.001));
      expect(prefs.hasFeedback, true);
    });

    test('disliked history creates negative bias', () {
      final prefs = service.buildPreferences(
        closetItems: [],
        historyRows: [
          _historyRow(
            liked: false,
            userColor: 'red',
            userCategory: 'Shirt',
            recItems: [
              {'category': 'Pants', 'color': 'green', 'style': 'formal'},
            ],
          ),
        ],
      );
      expect(prefs.colorPairBias['green|red'], closeTo(-0.1, 0.001));
      expect(prefs.categoryPairBias['Pants|Shirt'], closeTo(-0.1, 0.001));
    });

    test('null liked is ignored', () {
      final prefs = service.buildPreferences(
        closetItems: [],
        historyRows: [
          _historyRow(
            liked: null,
            userColor: 'blue',
            userCategory: 'T-shirt',
            recItems: [
              {'category': 'Jeans', 'color': 'black', 'style': 'casual'},
            ],
          ),
        ],
      );
      expect(prefs.colorPairBias, isEmpty);
      expect(prefs.categoryPairBias, isEmpty);
    });

    test('repeated likes accumulate and clamp at 1.0', () {
      final rows = List.generate(
        15,
        (_) => _historyRow(
          liked: true,
          userColor: 'blue',
          userCategory: 'T-shirt',
          recItems: [
            {'category': 'Jeans', 'color': 'black', 'style': 'casual'},
          ],
        ),
      );
      final prefs = service.buildPreferences(
        closetItems: [],
        historyRows: rows,
      );
      expect(prefs.colorPairBias['black|blue'], 1.0);
    });

    test('mixed feedback cancels out', () {
      final prefs = service.buildPreferences(
        closetItems: [],
        historyRows: [
          _historyRow(
            liked: true,
            userColor: 'blue',
            userCategory: 'T-shirt',
            recItems: [
              {'category': 'Jeans', 'color': 'black', 'style': 'casual'},
            ],
          ),
          _historyRow(
            liked: false,
            userColor: 'blue',
            userCategory: 'T-shirt',
            recItems: [
              {'category': 'Jeans', 'color': 'black', 'style': 'casual'},
            ],
          ),
        ],
      );
      expect(prefs.colorPairBias['black|blue'], closeTo(0.0, 0.001));
    });
  });
}

/// Helper to build a history row matching Supabase format.
Map<String, dynamic> _historyRow({
  required bool? liked,
  required String userColor,
  required String userCategory,
  required List<Map<String, String>> recItems,
}) {
  return {
    'id': 'test-id',
    'liked': liked,
    'recommendations_json': {
      'user_item': {
        'category': userCategory,
        'color': userColor,
        'style': 'casual',
        'confidence': 0.9,
      },
      'recommendations': [
        {
          'items': recItems,
          'match_score': 0.8,
          'match_reason': 'test',
          'color_harmony': 'test',
          'style_consistency': 'test',
        },
      ],
    },
    'created_at': '2026-04-04T00:00:00Z',
  };
}
