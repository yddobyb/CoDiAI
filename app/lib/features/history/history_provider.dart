import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../services/history_service.dart';
import '../../providers/service_providers.dart';

class HistoryState {
  final List<HistoryEntry> entries;
  final bool isLoading;
  final String? error;

  const HistoryState({
    this.entries = const [],
    this.isLoading = false,
    this.error,
  });

  HistoryState copyWith({
    List<HistoryEntry>? entries,
    bool? isLoading,
    String? error,
  }) {
    return HistoryState(
      entries: entries ?? this.entries,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

class HistoryNotifier extends Notifier<HistoryState> {
  @override
  HistoryState build() => const HistoryState();

  Future<void> loadHistory() async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final service = ref.read(historyServiceProvider);
      final rows = await service.fetchHistory();
      final entries = rows.map(HistoryService.parseEntry).toList();
      state = HistoryState(entries: entries);
    } catch (e) {
      debugPrint('[History] Load failed: $e');
      state = state.copyWith(isLoading: false, error: 'Failed to load history');
    }
  }

  Future<void> toggleLiked(String historyId, bool liked) async {
    try {
      final service = ref.read(historyServiceProvider);
      await service.updateLiked(historyId, liked);
      state = state.copyWith(
        entries: state.entries.map((e) {
          if (e.id == historyId) {
            return HistoryEntry(
              id: e.id,
              userItem: e.userItem,
              recommendations: e.recommendations,
              liked: e.liked == liked ? null : liked,
              createdAt: e.createdAt,
            );
          }
          return e;
        }).toList(),
      );
    } catch (e) {
      debugPrint('[History] Toggle liked failed: $e');
    }
  }
}

final historyProvider = NotifierProvider<HistoryNotifier, HistoryState>(
  HistoryNotifier.new,
);
