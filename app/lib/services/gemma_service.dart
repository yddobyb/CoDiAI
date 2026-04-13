import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter_gemma/flutter_gemma.dart';

class GemmaService {
  static const _modelUrl =
      'https://huggingface.co/nicoboss/gemma-4-E2B-it-GGUF/resolve/main/gemma-4-E2B-it-Q4_K_M.gguf';
  static const _modelId = 'gemma-4-E2B-it-Q4_K_M.gguf';

  bool _isModelLoaded = false;
  InferenceModel? _model;

  bool get isModelLoaded => _isModelLoaded;

  Future<bool> isModelInstalled() async {
    try {
      return await FlutterGemma.isModelInstalled(_modelId);
    } catch (e) {
      debugPrint('[Gemma] isModelInstalled error: $e');
      return false;
    }
  }

  Stream<double> downloadModel() {
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
          debugPrint('[Gemma] Download complete');
          controller.close();
        })
        .catchError((Object e) {
          debugPrint('[Gemma] Download error: $e');
          controller.addError(e);
          controller.close();
        });
    return controller.stream;
  }

  Future<void> loadModel() async {
    if (_isModelLoaded) return;
    _model = await FlutterGemma.getActiveModel(maxTokens: 512);
    _isModelLoaded = true;
    debugPrint('[Gemma] Model loaded');
  }

  Future<String?> generate(String prompt) async {
    if (!_isModelLoaded || _model == null) return null;
    final chat = await _model!.createChat();
    await chat.addQueryChunk(Message.text(text: prompt, isUser: true));
    final response = await chat.generateChatResponse();
    if (response is TextResponse) {
      final text = response.token.trim();
      return text.isEmpty ? null : text;
    }
    return null;
  }

  Future<void> unloadModel() async {
    await _model?.close();
    _model = null;
    _isModelLoaded = false;
    debugPrint('[Gemma] Model unloaded');
  }

  Future<void> deleteModel() async {
    await unloadModel();
    await FlutterGemma.uninstallModel(_modelId);
    debugPrint('[Gemma] Model deleted');
  }
}
