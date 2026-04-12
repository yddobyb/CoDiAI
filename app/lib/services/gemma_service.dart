import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter_gemma/flutter_gemma.dart';

/// Manages Gemma 4 E2B model lifecycle: download, load, and inference.
class GemmaService {
  static const _modelUrl =
      'https://huggingface.co/nicoboss/gemma-4-E2B-it-GGUF/resolve/main/gemma-4-E2B-it-Q4_K_M.gguf';
  static const _modelId = 'gemma-4-E2B-it-Q4_K_M.gguf';

  bool _isModelLoaded = false;
  InferenceModel? _model;

  bool get isModelLoaded => _isModelLoaded;

  /// Check if the model file is already downloaded.
  Future<bool> isModelInstalled() async {
    try {
      return await FlutterGemma.isModelInstalled(_modelId);
    } catch (e) {
      debugPrint('[Gemma] isModelInstalled check failed: $e');
      return false;
    }
  }

  /// Download the model. Yields progress (0.0 – 1.0).
  Stream<double> downloadModel() {
    debugPrint('[Gemma] Starting model download...');
    final controller = StreamController<double>();

    FlutterGemma.installModel(
      modelType: ModelType.gemmaIt,
      fileType: ModelFileType.binary,
    )
        .fromNetwork(_modelUrl)
        .withProgress((progress) {
          controller.add(progress / 100.0);
        })
        .install()
        .then((_) {
          debugPrint('[Gemma] Model download complete');
          controller.close();
        })
        .catchError((Object e) {
          debugPrint('[Gemma] Download error: $e');
          controller.addError(e);
          controller.close();
        });

    return controller.stream;
  }

  /// Load the model into memory for inference.
  Future<void> loadModel() async {
    if (_isModelLoaded) return;
    try {
      debugPrint('[Gemma] Loading model...');
      _model = await FlutterGemma.getActiveModel(maxTokens: 512);
      _isModelLoaded = true;
      debugPrint('[Gemma] Model loaded');
    } catch (e) {
      debugPrint('[Gemma] Load error: $e');
      _isModelLoaded = false;
      rethrow;
    }
  }

  /// Generate a text response from the model.
  Future<String?> generate(String prompt) async {
    if (!_isModelLoaded || _model == null) {
      debugPrint('[Gemma] Model not loaded');
      return null;
    }

    try {
      final chat = await _model!.createChat();
      await chat.addQueryChunk(Message.text(text: prompt, isUser: true));
      final response = await chat.generateChatResponse();
      if (response is TextResponse) {
        final text = response.token.trim();
        debugPrint('[Gemma] Generated ${text.length} chars');
        return text.isEmpty ? null : text;
      }
      debugPrint('[Gemma] Unexpected response type: ${response.runtimeType}');
      return null;
    } catch (e) {
      debugPrint('[Gemma] Generate error: $e');
      return null;
    }
  }

  /// Unload the model from memory.
  Future<void> unloadModel() async {
    try {
      await _model?.close();
    } catch (_) {}
    _model = null;
    _isModelLoaded = false;
    debugPrint('[Gemma] Model unloaded');
  }

  /// Delete the downloaded model file.
  Future<void> deleteModel() async {
    await unloadModel();
    try {
      await FlutterGemma.uninstallModel(_modelId);
      debugPrint('[Gemma] Model deleted');
    } catch (e) {
      debugPrint('[Gemma] Delete error: $e');
    }
  }
}
