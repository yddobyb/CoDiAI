import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import '../core/config/api_keys.dart' as config;
import '../models/outfit_recommendation.dart';
import 'gemma_service.dart';

class LlmService {
  final GemmaService? _gemma;

  LlmService({GemmaService? gemmaService}) : _gemma = gemmaService;

  static const _baseUrl = 'https://generativelanguage.googleapis.com/v1beta/models';

  bool get isAvailable => config.geminiApiKey.isNotEmpty || (_gemma?.isModelLoaded ?? false);
  bool get isGemmaReady => _gemma?.isModelLoaded ?? false;

  /// Build the style tip prompt from a recommendation.
  String _buildPrompt(OutfitRecommendation rec) {
    final userItem = rec.userItem;
    final items = rec.recommendedItems;
    final itemsDesc = items.map((i) => '${i.color} ${i.category}').join(' + ');

    return '''You are a fashion stylist. A user has a ${userItem.color} ${userItem.category} (${userItem.style} style).
The recommended outfit combination is: ${userItem.color} ${userItem.category} + $itemsDesc.
Match score: ${rec.matchPercent}%.
Color harmony: ${rec.colorHarmony}.
Style: ${rec.styleConsistency}.

Write a 2-3 sentence styling tip. Include when/where to wear this outfit, one specific styling tip, and the overall vibe. Keep it concise and practical. Do not use emojis.''';
  }

  /// Generate styling description — tries Gemma on-device first, then Gemini API.
  Future<String?> generateDescription(OutfitRecommendation rec) async {
    if (!isAvailable) return null;

    final prompt = _buildPrompt(rec);

    // Try Gemma on-device first
    if (isGemmaReady) {
      try {
        debugPrint('[LLM] Trying Gemma on-device...');
        final stopwatch = Stopwatch()..start();
        final result = await _gemma!.generate(prompt);
        stopwatch.stop();
        if (result != null && result.isNotEmpty) {
          debugPrint('[LLM] Gemma success in ${stopwatch.elapsedMilliseconds}ms');
          return result;
        }
      } catch (e) {
        debugPrint('[LLM] Gemma error, falling back to API: $e');
      }
    }

    // Fallback to Gemini API
    if (config.geminiApiKey.isNotEmpty) {
      return _callGeminiWithFallback(prompt);
    }

    return null;
  }

  /// Stream tokens for a styling description.
  /// Yields token deltas via Gemma on-device; falls back to a single-chunk Gemini emission.
  Stream<String> generateDescriptionStream(OutfitRecommendation rec) async* {
    if (!isAvailable) return;

    final prompt = _buildPrompt(rec);

    if (isGemmaReady) {
      try {
        debugPrint('[LLM] Streaming via Gemma on-device...');
        final sw = Stopwatch()..start();
        var emitted = false;
        await for (final token in _gemma!.generateStream(prompt)) {
          emitted = true;
          yield token;
        }
        sw.stop();
        if (emitted) {
          debugPrint('[LLM] Gemma stream done in ${sw.elapsedMilliseconds}ms');
          return;
        }
      } catch (e) {
        debugPrint('[LLM] Gemma stream error, falling back to Gemini: $e');
      }
    }

    if (config.geminiApiKey.isNotEmpty) {
      final text = await _callGeminiWithFallback(prompt);
      if (text != null && text.isNotEmpty) yield text;
    }
  }

  Future<String?> _callGeminiWithFallback(String prompt) async {
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

  /// Generate descriptions for multiple recommendations.
  /// When Gemma is loaded, tokens stream into each rec's `llmDescription` and
  /// `onUpdate` fires per token so the UI can render progressively.
  /// With Gemini only, runs in parallel and fires `onUpdate` once at the end.
  Future<void> generateAll(
    List<OutfitRecommendation> recs, {
    void Function()? onUpdate,
  }) async {
    if (!isAvailable) return;

    if (isGemmaReady) {
      for (final rec in recs) {
        var buffer = '';
        await for (final token in generateDescriptionStream(rec)) {
          buffer += token;
          rec.llmDescription = buffer;
          onUpdate?.call();
        }
        final finalText = buffer.trim();
        rec.llmDescription = finalText.isEmpty ? null : finalText;
        onUpdate?.call();
      }
    } else {
      final results = await Future.wait(recs.map((r) => generateDescription(r)));
      for (var i = 0; i < recs.length; i++) {
        recs[i].llmDescription = results[i];
      }
      onUpdate?.call();
    }
  }

  /// Parse a natural language query into structured product filters using Gemma.
  /// Returns null if Gemma is not available or parsing fails.
  Future<Map<String, String>?> parseSearchQuery(String query) async {
    if (!isGemmaReady) return null;

    final prompt = '''Parse this fashion search query into structured filters.
Available categories: T-shirt, Shirt, Hoodie, Sweater, Jacket, Coat, Pants, Jeans, Shorts, Skirt, Dress, Sneakers, Boots, Flats, Heels
Available colors: black, white, gray, beige, navy, brown, blue, red, green, pink, yellow, purple
Available styles: casual, formal, sporty
Available seasons: spring, summer, fall, winter

Query: "$query"

Respond ONLY with a JSON object. Example: {"category":"Boots","color":"black","style":"casual"}
Only include fields that are clearly mentioned or implied. Do not guess.''';

    try {
      final result = await _gemma!.generate(prompt);
      if (result == null) return null;

      // Extract JSON from response
      final jsonMatch = RegExp(r'\{[^}]+\}').firstMatch(result);
      if (jsonMatch == null) return null;

      final parsed = jsonDecode(jsonMatch.group(0)!) as Map<String, dynamic>;
      return parsed.map((k, v) => MapEntry(k, v.toString()));
    } catch (e) {
      debugPrint('[LLM] Search query parse error: $e');
      return null;
    }
  }
}
