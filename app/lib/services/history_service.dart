import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../models/clothing_item.dart';
import '../models/outfit_recommendation.dart';

class HistoryService {
  final SupabaseClient _client = Supabase.instance.client;

  String get _userId => _client.auth.currentUser!.id;

  Future<void> saveHistory({
    required ClothingItem userItem,
    required List<OutfitRecommendation> recommendations,
    String? closetItemId,
  }) async {
    final recsJson = recommendations.map((r) => <String, dynamic>{
      'items': r.recommendedItems.map((i) => <String, dynamic>{
        'category': i.category,
        'color': i.color,
        'style': i.style,
      }).toList(),
      'match_score': r.matchScore,
      'match_reason': r.matchReason,
      'color_harmony': r.colorHarmony,
      'style_consistency': r.styleConsistency,
      'llm_description': r.llmDescription,
    }).toList();

    final jsonData = <String, dynamic>{
      'user_item': <String, dynamic>{
        'category': userItem.category,
        'color': userItem.color,
        'style': userItem.style,
        'confidence': userItem.confidence,
      },
      'recommendations': recsJson,
    };

    await _client.from('outfit_history').insert({
      'user_id': _userId,
      'user_item_id': closetItemId,
      'recommendations_json': jsonData,
      'liked': null,
    });

    debugPrint('[History] Saved ${recommendations.length} recommendations');
  }

  Future<List<Map<String, dynamic>>> fetchHistory() async {
    final data = await _client
        .from('outfit_history')
        .select()
        .eq('user_id', _userId)
        .order('created_at', ascending: false)
        .limit(50);
    return List<Map<String, dynamic>>.from(data);
  }

  Future<void> updateLiked(String historyId, bool liked) async {
    await _client
        .from('outfit_history')
        .update({'liked': liked})
        .eq('id', historyId);
    debugPrint('[History] Updated liked=$liked for $historyId');
  }

  /// Parse stored JSON back into displayable data.
  static HistoryEntry parseEntry(Map<String, dynamic> row) {
    final json = row['recommendations_json'];
    final Map<String, dynamic> data;
    if (json is String) {
      data = jsonDecode(json) as Map<String, dynamic>;
    } else {
      data = Map<String, dynamic>.from(json as Map);
    }

    final userItemData = data['user_item'] as Map<String, dynamic>;
    final userItem = ClothingItem(
      category: userItemData['category'] as String,
      color: userItemData['color'] as String,
      style: userItemData['style'] as String,
      confidence: (userItemData['confidence'] as num?)?.toDouble() ?? 0.0,
    );

    final recsList = data['recommendations'] as List;
    final recommendations = recsList.map((r) {
      final rMap = r as Map<String, dynamic>;
      final items = (rMap['items'] as List).map((i) {
        final iMap = i as Map<String, dynamic>;
        return ClothingItem(
          category: iMap['category'] as String,
          color: iMap['color'] as String,
          style: iMap['style'] as String,
        );
      }).toList();

      return OutfitRecommendation(
        userItem: userItem,
        recommendedItems: items,
        matchScore: (rMap['match_score'] as num).toDouble(),
        categoryScore: 0,
        colorScore: 0,
        styleScore: 0,
        matchReason: rMap['match_reason'] as String? ?? '',
        colorHarmony: rMap['color_harmony'] as String? ?? '',
        styleConsistency: rMap['style_consistency'] as String? ?? '',
        llmDescription: rMap['llm_description'] as String?,
      );
    }).toList();

    return HistoryEntry(
      id: row['id'] as String,
      userItem: userItem,
      recommendations: recommendations,
      liked: row['liked'] as bool?,
      createdAt: DateTime.parse(row['created_at'] as String),
    );
  }
}

class HistoryEntry {
  final String id;
  final ClothingItem userItem;
  final List<OutfitRecommendation> recommendations;
  final bool? liked;
  final DateTime createdAt;

  const HistoryEntry({
    required this.id,
    required this.userItem,
    required this.recommendations,
    required this.liked,
    required this.createdAt,
  });
}
