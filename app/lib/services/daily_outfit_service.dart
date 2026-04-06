import 'dart:math';
import 'package:flutter/foundation.dart';
import '../models/clothing_item.dart';
import '../models/outfit_recommendation.dart';
import 'recommendation_service.dart';

class DailyOutfitService {
  final RecommendationService _recService = RecommendationService();

  /// Get current season based on month (Northern hemisphere / Canada).
  static String get currentSeason {
    final month = DateTime.now().month;
    if (month >= 3 && month <= 5) return 'spring';
    if (month >= 6 && month <= 8) return 'summer';
    if (month >= 9 && month <= 11) return 'fall';
    return 'winter';
  }

  /// Pick a closet item for today's outfit and generate a recommendation.
  /// Uses a deterministic seed based on date so the same outfit shows all day.
  Future<OutfitRecommendation?> generateDailyOutfit({
    required List<Map<String, dynamic>> closetItems,
    String? preferredStyle,
  }) async {
    if (closetItems.isEmpty) return null;

    // Deterministic random based on today's date
    final today = DateTime.now();
    final seed = today.year * 10000 + today.month * 100 + today.day;
    final rng = Random(seed);

    // Prefer items matching current season, but fall back to all items
    final season = currentSeason;
    final seasonalItems = closetItems.where((item) {
      final cat = item['category'] as String;
      return _fitsCurrentSeason(cat, season);
    }).toList();

    final pool = seasonalItems.isNotEmpty ? seasonalItems : closetItems;
    final picked = pool[rng.nextInt(pool.length)];

    final clothingItem = ClothingItem(
      category: picked['category'] as String,
      color: picked['color'] as String,
      style: picked['style'] as String? ?? 'casual',
      confidence: (picked['confidence'] as num?)?.toDouble() ?? 0.8,
      imagePath: picked['image_url'] as String?,
    );

    debugPrint('[DailyOutfit] Picked ${clothingItem.color} ${clothingItem.category} '
        'for $season (pool: ${pool.length}/${closetItems.length})');

    // Generate one recommendation
    final recs = _recService.recommend(
      clothingItem,
      preferredStyle: preferredStyle,
    );

    if (recs.isEmpty) return null;
    return recs.first;
  }

  bool _fitsCurrentSeason(String category, String season) {
    switch (season) {
      case 'summer':
        return ['T-shirt', 'Shirt', 'Shorts', 'Skirt', 'Dress',
                'Sneakers', 'Flats', 'Heels'].contains(category);
      case 'winter':
        return ['Sweater', 'Hoodie', 'Coat', 'Jacket', 'Jeans',
                'Pants', 'Boots'].contains(category);
      case 'spring':
      case 'fall':
        return ['T-shirt', 'Shirt', 'Sweater', 'Jacket', 'Jeans',
                'Pants', 'Skirt', 'Sneakers', 'Boots', 'Flats'].contains(category);
      default:
        return true;
    }
  }
}
