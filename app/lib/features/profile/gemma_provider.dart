import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../providers/service_providers.dart';

enum GemmaDownloadStatus { notDownloaded, downloading, installed }

class GemmaState {
  final GemmaDownloadStatus downloadStatus;
  final double downloadProgress;
  final bool isModelReady;
  final bool isGenerating;
  final String? error;

  const GemmaState({
    this.downloadStatus = GemmaDownloadStatus.notDownloaded,
    this.downloadProgress = 0.0,
    this.isModelReady = false,
    this.isGenerating = false,
    this.error,
  });

  bool get isEnabled => downloadStatus == GemmaDownloadStatus.installed && isModelReady;

  GemmaState copyWith({
    GemmaDownloadStatus? downloadStatus,
    double? downloadProgress,
    bool? isModelReady,
    bool? isGenerating,
    String? error,
    bool clearError = false,
  }) {
    return GemmaState(
      downloadStatus: downloadStatus ?? this.downloadStatus,
      downloadProgress: downloadProgress ?? this.downloadProgress,
      isModelReady: isModelReady ?? this.isModelReady,
      isGenerating: isGenerating ?? this.isGenerating,
      error: clearError ? null : (error ?? this.error),
    );
  }
}

class GemmaNotifier extends Notifier<GemmaState> {
  static const _prefKey = 'offline_ai_enabled';

  @override
  GemmaState build() {
    _checkInitialState();
    return const GemmaState();
  }

  Future<void> _checkInitialState() async {
    final gemma = ref.read(gemmaServiceProvider);
    final installed = await gemma.isModelInstalled();
    if (installed) {
      state = state.copyWith(downloadStatus: GemmaDownloadStatus.installed);
      // Auto-load if user had it enabled
      final prefs = await SharedPreferences.getInstance();
      if (prefs.getBool(_prefKey) ?? false) {
        await loadModel();
      }
    }
  }

  Future<void> downloadAndEnable() async {
    final gemma = ref.read(gemmaServiceProvider);
    state = state.copyWith(
      downloadStatus: GemmaDownloadStatus.downloading,
      downloadProgress: 0.0,
      clearError: true,
    );

    try {
      await for (final progress in gemma.downloadModel()) {
        state = state.copyWith(downloadProgress: progress);
      }
      state = state.copyWith(downloadStatus: GemmaDownloadStatus.installed);
      await loadModel();
      final prefs = await SharedPreferences.getInstance();
      await prefs.setBool(_prefKey, true);
    } catch (e) {
      state = state.copyWith(
        downloadStatus: GemmaDownloadStatus.notDownloaded,
        error: 'Download failed: $e',
      );
    }
  }

  Future<void> loadModel() async {
    final gemma = ref.read(gemmaServiceProvider);
    try {
      await gemma.loadModel();
      state = state.copyWith(isModelReady: true);
    } catch (e) {
      state = state.copyWith(
        isModelReady: false,
        error: 'Failed to load model: $e',
      );
    }
  }

  Future<void> disable() async {
    final gemma = ref.read(gemmaServiceProvider);
    await gemma.unloadModel();
    state = state.copyWith(isModelReady: false);
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_prefKey, false);
  }

  Future<void> deleteModel() async {
    final gemma = ref.read(gemmaServiceProvider);
    await gemma.deleteModel();
    state = const GemmaState();
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_prefKey, false);
  }
}

final gemmaProvider = NotifierProvider<GemmaNotifier, GemmaState>(
  GemmaNotifier.new,
);
