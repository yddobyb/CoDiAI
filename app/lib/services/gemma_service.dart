import 'dart:async';
import 'dart:io';
import 'package:flutter/widgets.dart';
import 'package:flutter_gemma/flutter_gemma.dart';
import 'package:path_provider/path_provider.dart';

enum GemmaUnloadReason { manual, memoryPressure }

enum GemmaIntegrityResult { ok, missingFile, tooSmall, badFormat, unknown }

class GemmaService with WidgetsBindingObserver {
  static const _modelUrl =
      'https://huggingface.co/nicoboss/gemma-4-E2B-it-GGUF/resolve/main/gemma-4-E2B-it-Q4_K_M.gguf';
  static const _modelId = 'gemma-4-E2B-it-Q4_K_M.gguf';

  bool _isModelLoaded = false;
  InferenceModel? _model;
  bool _observerAttached = false;
  final _stateController = StreamController<bool>.broadcast();
  final _unloadReasonController = StreamController<GemmaUnloadReason>.broadcast();

  GemmaService() {
    _attachObserver();
  }

  void _attachObserver() {
    if (_observerAttached) return;
    WidgetsBinding.instance.addObserver(this);
    _observerAttached = true;
  }

  bool get isModelLoaded => _isModelLoaded;

  /// Emits [true] when the model finishes loading, [false] when it's unloaded
  /// (manually or due to memory pressure).
  Stream<bool> get modelStateStream => _stateController.stream;

  /// Emits each time the model is unloaded, with the reason.
  Stream<GemmaUnloadReason> get unloadReasonStream => _unloadReasonController.stream;

  @override
  void didHaveMemoryPressure() {
    if (!_isModelLoaded) return;
    debugPrint('[Gemma] Memory pressure — auto-unloading model');
    unawaited(_autoUnload());
  }

  Future<void> _autoUnload() async {
    if (!_isModelLoaded) return;
    try {
      await _model?.close();
    } catch (e) {
      debugPrint('[Gemma] Auto-unload close error: $e');
    }
    _model = null;
    _isModelLoaded = false;
    _unloadReasonController.add(GemmaUnloadReason.memoryPressure);
    _stateController.add(false);
  }

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
    _stateController.add(true);
    debugPrint('[Gemma] Model loaded');
  }

  /// Minimum plausible size for a usable Q4_K_M Gemma build (in bytes).
  /// The real file is >1.5 GB — this is a floor to catch truncated / error-page responses.
  static const int _minModelBytes = 512 * 1024 * 1024; // 512 MB

  /// GGUF magic bytes at offset 0 of a valid file.
  static const List<int> _ggufMagic = [0x47, 0x47, 0x55, 0x46]; // "GGUF"

  /// Verify the installed model is complete and in the expected format.
  /// Called after download and at startup to catch corrupt / truncated downloads.
  Future<GemmaIntegrityResult> verifyInstalledModel() async {
    try {
      final dir = await getApplicationDocumentsDirectory();
      final file = File('${dir.path}/$_modelId');
      if (!await file.exists()) return GemmaIntegrityResult.missingFile;

      final size = await file.length();
      if (size < _minModelBytes) return GemmaIntegrityResult.tooSmall;

      final raf = await file.open();
      try {
        final header = await raf.read(4);
        for (var i = 0; i < 4; i++) {
          if (header[i] != _ggufMagic[i]) return GemmaIntegrityResult.badFormat;
        }
      } finally {
        await raf.close();
      }
      return GemmaIntegrityResult.ok;
    } catch (e) {
      debugPrint('[Gemma] verifyInstalledModel error: $e');
      return GemmaIntegrityResult.unknown;
    }
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

  Stream<String> generateStream(String prompt) async* {
    if (!_isModelLoaded || _model == null) return;
    final chat = await _model!.createChat();
    await chat.addQueryChunk(Message.text(text: prompt, isUser: true));
    await for (final resp in chat.generateChatResponseAsync()) {
      if (resp is TextResponse && resp.token.isNotEmpty) {
        yield resp.token;
      }
    }
  }

  Future<void> unloadModel() async {
    final wasLoaded = _isModelLoaded;
    await _model?.close();
    _model = null;
    _isModelLoaded = false;
    if (wasLoaded) {
      _unloadReasonController.add(GemmaUnloadReason.manual);
      _stateController.add(false);
    }
    debugPrint('[Gemma] Model unloaded');
  }

  Future<void> deleteModel() async {
    await unloadModel();
    await FlutterGemma.uninstallModel(_modelId);
    debugPrint('[Gemma] Model deleted');
  }

  void dispose() {
    if (_observerAttached) {
      WidgetsBinding.instance.removeObserver(this);
      _observerAttached = false;
    }
    _stateController.close();
    _unloadReasonController.close();
  }
}
