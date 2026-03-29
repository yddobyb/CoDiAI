import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../models/clothing_item.dart';
import '../../providers/service_providers.dart';

enum AnalysisStatus { idle, loadingModel, analyzing, done, error }

class AnalysisState {
  final AnalysisStatus status;
  final ClothingItem? result;
  final String? errorMessage;

  const AnalysisState({
    this.status = AnalysisStatus.idle,
    this.result,
    this.errorMessage,
  });

  AnalysisState copyWith({
    AnalysisStatus? status,
    ClothingItem? result,
    String? errorMessage,
  }) {
    return AnalysisState(
      status: status ?? this.status,
      result: result ?? this.result,
      errorMessage: errorMessage,
    );
  }
}

class AnalysisNotifier extends Notifier<AnalysisState> {
  @override
  AnalysisState build() => const AnalysisState();

  Future<void> loadModelAndAnalyze(String imagePath) async {
    final ml = ref.read(mlServiceProvider);

    try {
      state = state.copyWith(status: AnalysisStatus.loadingModel);
      await ml.loadModel();

      state = state.copyWith(status: AnalysisStatus.analyzing);
      final result = await ml.predict(imagePath);
      state = AnalysisState(status: AnalysisStatus.done, result: result);
    } catch (e) {
      state = AnalysisState(
        status: AnalysisStatus.error,
        errorMessage: e.toString(),
      );
    }
  }

  void reset() => state = const AnalysisState();
}

final analysisProvider =
    NotifierProvider<AnalysisNotifier, AnalysisState>(
  AnalysisNotifier.new,
);
