import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../providers/service_providers.dart';

class ClosetState {
  final List<Map<String, dynamic>> items;
  final bool isLoading;
  final String? error;

  const ClosetState({
    this.items = const [],
    this.isLoading = false,
    this.error,
  });

  ClosetState copyWith({
    List<Map<String, dynamic>>? items,
    bool? isLoading,
    String? error,
  }) {
    return ClosetState(
      items: items ?? this.items,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

class ClosetNotifier extends Notifier<ClosetState> {
  @override
  ClosetState build() => const ClosetState();

  Future<void> loadItems() async {
    state = state.copyWith(isLoading: true);
    try {
      final service = ref.read(closetServiceProvider);
      final items = await service.fetchItems();
      state = ClosetState(items: items);
    } catch (e) {
      debugPrint('[Closet] Load error: $e');
      state = state.copyWith(isLoading: false, error: 'Failed to load closet');
    }
  }

  Future<void> addItem({
    required String imagePath,
    required String category,
    required String color,
    required String style,
    required double confidence,
  }) async {
    try {
      final service = ref.read(closetServiceProvider);
      final item = await service.addItem(
        imagePath: imagePath,
        category: category,
        color: color,
        style: style,
        confidence: confidence,
      );
      state = ClosetState(items: [item, ...state.items]);
    } catch (e) {
      debugPrint('[Closet] Add error: $e');
    }
  }

  Future<void> deleteItem(String id) async {
    try {
      final service = ref.read(closetServiceProvider);
      await service.deleteItem(id);
      state = ClosetState(
        items: state.items.where((i) => i['id'] != id).toList(),
      );
    } catch (e) {
      debugPrint('[Closet] Delete error: $e');
    }
  }
}

final closetProvider = NotifierProvider<ClosetNotifier, ClosetState>(
  ClosetNotifier.new,
);
