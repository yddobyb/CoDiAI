import 'package:flutter_test/flutter_test.dart';
import 'package:fashion_codi/features/analysis/analysis_provider.dart';

void main() {
  group('AnalysisState', () {
    test('default state is idle with no result', () {
      const state = AnalysisState();
      expect(state.status, AnalysisStatus.idle);
      expect(state.result, isNull);
      expect(state.errorMessage, isNull);
    });

    test('copyWith preserves unchanged fields', () {
      const state = AnalysisState(status: AnalysisStatus.analyzing);
      final copied = state.copyWith(status: AnalysisStatus.done);
      expect(copied.status, AnalysisStatus.done);
      expect(copied.result, isNull);
    });

    test('copyWith clears errorMessage when not provided', () {
      const state = AnalysisState(
        status: AnalysisStatus.error,
        errorMessage: 'Something went wrong',
      );
      final copied = state.copyWith(status: AnalysisStatus.analyzing);
      expect(copied.errorMessage, isNull);
    });
  });

  group('AnalysisStatus', () {
    test('has all expected values', () {
      expect(AnalysisStatus.values, containsAll([
        AnalysisStatus.idle,
        AnalysisStatus.loadingModel,
        AnalysisStatus.analyzing,
        AnalysisStatus.done,
        AnalysisStatus.error,
      ]));
    });
  });
}
