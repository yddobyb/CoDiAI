import 'dart:convert';
import 'package:flutter/foundation.dart';
import '../models/user_preferences.dart';

/// Builds [UserPreferences] from raw closet items and history feedback data.
class PersonalizationService {
  /// Construct preferences from Supabase row data.
  ///
  /// [closetItems] — rows from closet_items table (need 'color', 'style' keys).
  /// [historyRows] — rows from outfit_history table (need 'liked', 'recommendations_json').
  UserPreferences buildPreferences({
    required List<Map<String, dynamic>> closetItems,
    required List<Map<String, dynamic>> historyRows,
    String? profileStyle,
  }) {
    final colorAffinity = _buildColorAffinity(closetItems);
    final styleAffinity = _buildStyleAffinity(closetItems);
    final (colorPairBias, categoryPairBias) = _buildFeedbackBias(historyRows);

    debugPrint('[Personalization] Built preferences — '
        'closet: ${closetItems.length} items, '
        'colors: ${colorAffinity.length}, styles: ${styleAffinity.length}, '
        'feedback entries: ${historyRows.where((r) => r['liked'] != null).length}');

    return UserPreferences(
      profileStyle: profileStyle,
      colorAffinity: colorAffinity,
      styleAffinity: styleAffinity,
      colorPairBias: colorPairBias,
      categoryPairBias: categoryPairBias,
    );
  }

  /// Normalized color frequency (0–1) from closet items.
  Map<String, double> _buildColorAffinity(List<Map<String, dynamic>> items) {
    if (items.isEmpty) return {};
    final counts = <String, int>{};
    for (final item in items) {
      final color = item['color'] as String?;
      if (color != null) {
        counts[color] = (counts[color] ?? 0) + 1;
      }
    }
    if (counts.isEmpty) return {};
    final maxCount = counts.values.reduce((a, b) => a > b ? a : b);
    return counts.map((k, v) => MapEntry(k, v / maxCount));
  }

  /// Normalized style frequency (0–1) from closet items.
  Map<String, double> _buildStyleAffinity(List<Map<String, dynamic>> items) {
    if (items.isEmpty) return {};
    final counts = <String, int>{};
    for (final item in items) {
      final style = item['style'] as String?;
      if (style != null) {
        counts[style] = (counts[style] ?? 0) + 1;
      }
    }
    if (counts.isEmpty) return {};
    final maxCount = counts.values.reduce((a, b) => a > b ? a : b);
    return counts.map((k, v) => MapEntry(k, v / maxCount));
  }

  /// Extract color-pair and category-pair biases from liked/disliked history.
  ///
  /// Each liked entry adds +0.1 per pair, disliked subtracts -0.1, clamped to [-1, 1].
  (Map<String, double>, Map<String, double>) _buildFeedbackBias(
      List<Map<String, dynamic>> historyRows) {
    final colorPairBias = <String, double>{};
    final categoryPairBias = <String, double>{};

    for (final row in historyRows) {
      final liked = row['liked'] as bool?;
      if (liked == null) continue;

      final json = row['recommendations_json'];
      if (json == null) continue;

      final Map<String, dynamic> data;
      try {
        if (json is String) {
          data = Map<String, dynamic>.from(jsonDecode(json) as Map);
        } else {
          data = Map<String, dynamic>.from(json as Map);
        }
      } catch (_) {
        continue;
      }

      final userItemData = data['user_item'] as Map<String, dynamic>?;
      if (userItemData == null) continue;
      final userColor = userItemData['color'] as String?;
      final userCategory = userItemData['category'] as String?;
      if (userColor == null || userCategory == null) continue;

      final recsList = data['recommendations'] as List?;
      if (recsList == null) continue;

      final delta = liked ? 0.1 : -0.1;

      for (final rec in recsList) {
        final rMap = rec as Map<String, dynamic>;
        final items = rMap['items'] as List?;
        if (items == null) continue;

        for (final item in items) {
          final iMap = item as Map<String, dynamic>;
          final recColor = iMap['color'] as String?;
          final recCategory = iMap['category'] as String?;
          if (recColor == null || recCategory == null) continue;

          final colorKey = _sortedPairKey(userColor, recColor);
          final catKey = _sortedPairKey(userCategory, recCategory);

          colorPairBias[colorKey] =
              ((colorPairBias[colorKey] ?? 0) + delta).clamp(-1.0, 1.0);
          categoryPairBias[catKey] =
              ((categoryPairBias[catKey] ?? 0) + delta).clamp(-1.0, 1.0);
        }
      }
    }

    return (colorPairBias, categoryPairBias);
  }

  static String _sortedPairKey(String a, String b) {
    return a.compareTo(b) <= 0 ? '$a|$b' : '$b|$a';
  }
}
