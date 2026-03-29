import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import '../core/config/api_keys.dart' as config;
import '../models/outfit_recommendation.dart';

class LlmService {
  static const _baseUrl = 'https://generativelanguage.googleapis.com/v1beta/models';

  bool get isAvailable => config.geminiApiKey.isNotEmpty;

  Future<String?> _callGemini(String prompt, String model) async {
    final url = Uri.parse('$_baseUrl/$model:generateContent?key=${config.geminiApiKey}');

    final body = jsonEncode({
      'contents': [
        {
          'parts': [
            {'text': prompt}
          ]
        }
      ],
      'generationConfig': {
        'temperature': 0.7,
        'maxOutputTokens': 1024,
      },
    });

    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: body,
    );

    if (response.statusCode == 200) {
      try {
        final json = jsonDecode(response.body) as Map<String, dynamic>;
        final candidates = json['candidates'] as List?;
        if (candidates == null || candidates.isEmpty) return null;
        final content = (candidates[0] as Map?)?['content'] as Map?;
        final parts = content?['parts'] as List?;
        if (parts == null || parts.isEmpty) return null;
        final text = (parts[0] as Map?)?['text'] as String?;
        return text?.trim();
      } catch (e) {
        debugPrint('[LLM] $model JSON parse error: $e');
        return null;
      }
    } else {
      final preview = response.body.length > 200
          ? response.body.substring(0, 200)
          : response.body;
      debugPrint('[LLM] $model failed (${response.statusCode}): $preview');
      return null;
    }
  }

  /// Generate styling description for an outfit recommendation.
  Future<String?> generateDescription(OutfitRecommendation rec) async {
    if (!isAvailable) return null;

    final userItem = rec.userItem;
    final items = rec.recommendedItems;
    final itemsDesc = items.map((i) => '${i.color} ${i.category}').join(' + ');

    final prompt = '''You are a fashion stylist. A user has a ${userItem.color} ${userItem.category} (${userItem.style} style).
The recommended outfit combination is: ${userItem.color} ${userItem.category} + $itemsDesc.
Match score: ${rec.matchPercent}%.
Color harmony: ${rec.colorHarmony}.
Style: ${rec.styleConsistency}.

Write a 2-3 sentence styling tip. Include when/where to wear this outfit, one specific styling tip, and the overall vibe. Keep it concise and practical. Do not use emojis.''';

    // Try models in order
    final stopwatch = Stopwatch()..start();
    for (final model in ['gemini-2.5-flash', 'gemini-2.0-flash-lite', 'gemini-flash-latest']) {
      try {
        debugPrint('[LLM] Trying $model...');
        final result = await _callGemini(prompt, model);
        if (result != null && result.isNotEmpty) {
          stopwatch.stop();
          debugPrint('[LLM] Success with $model in ${stopwatch.elapsedMilliseconds}ms');
          return result;
        }
      } catch (e) {
        debugPrint('[LLM] $model error: $e');
      }
    }
    return null;
  }

  /// Generate descriptions for multiple recommendations in parallel.
  Future<void> generateAll(List<OutfitRecommendation> recs) async {
    if (!isAvailable) return;
    final results = await Future.wait(recs.map((r) => generateDescription(r)));
    for (var i = 0; i < recs.length; i++) {
      recs[i].llmDescription = results[i];
    }
  }
}
