import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../models/product.dart';
import '../../providers/service_providers.dart';

class ShopState {
  final List<Product> products;
  final bool isLoading;
  final bool hasMore;
  final String? error;
  final String? categoryFilter;
  final String? colorFilter;
  final String sortBy;
  final String? searchQuery;

  const ShopState({
    this.products = const [],
    this.isLoading = false,
    this.hasMore = true,
    this.error,
    this.categoryFilter,
    this.colorFilter,
    this.sortBy = 'created_at',
    this.searchQuery,
  });

  ShopState copyWith({
    List<Product>? products,
    bool? isLoading,
    bool? hasMore,
    String? error,
    String? categoryFilter,
    String? colorFilter,
    String? sortBy,
    String? searchQuery,
    bool clearCategory = false,
    bool clearColor = false,
    bool clearSearch = false,
    bool clearError = false,
  }) {
    return ShopState(
      products: products ?? this.products,
      isLoading: isLoading ?? this.isLoading,
      hasMore: hasMore ?? this.hasMore,
      error: clearError ? null : (error ?? this.error),
      categoryFilter: clearCategory ? null : (categoryFilter ?? this.categoryFilter),
      colorFilter: clearColor ? null : (colorFilter ?? this.colorFilter),
      sortBy: sortBy ?? this.sortBy,
      searchQuery: clearSearch ? null : (searchQuery ?? this.searchQuery),
    );
  }
}

class ShopNotifier extends Notifier<ShopState> {
  static const _pageSize = 20;

  @override
  ShopState build() => const ShopState();

  Future<void> loadProducts({bool refresh = false}) async {
    if (state.isLoading) return;

    state = state.copyWith(
      isLoading: true,
      clearError: true,
      products: refresh ? [] : null,
      hasMore: refresh ? true : null,
    );

    try {
      final service = ref.read(productServiceProvider);

      List<Product> products;
      if (state.searchQuery != null && state.searchQuery!.isNotEmpty) {
        products = await service.search(state.searchQuery!, limit: _pageSize);
        state = state.copyWith(products: products, isLoading: false, hasMore: false);
      } else {
        products = await service.fetchProducts(
          category: state.categoryFilter,
          color: state.colorFilter,
          sortBy: state.sortBy,
          ascending: state.sortBy == 'price',
          limit: _pageSize,
          offset: refresh ? 0 : state.products.length,
        );
        final merged = refresh ? products : [...state.products, ...products];
        state = state.copyWith(
          products: merged,
          isLoading: false,
          hasMore: products.length >= _pageSize,
        );
      }

      debugPrint('[Shop] Loaded ${state.products.length} products');
    } catch (e) {
      debugPrint('[Shop] Load error: $e');
      state = state.copyWith(isLoading: false, error: 'Failed to load products');
    }
  }

  void setCategory(String? category) {
    state = state.copyWith(
      categoryFilter: category,
      clearCategory: category == null,
      clearSearch: true,
    );
    loadProducts(refresh: true);
  }

  void setColor(String? color) {
    state = state.copyWith(
      colorFilter: color,
      clearColor: color == null,
    );
    loadProducts(refresh: true);
  }

  void setSort(String sortBy) {
    state = state.copyWith(sortBy: sortBy);
    loadProducts(refresh: true);
  }

  void search(String query) {
    state = state.copyWith(
      searchQuery: query,
      clearSearch: query.isEmpty,
      clearCategory: true,
      clearColor: true,
    );
    loadProducts(refresh: true);
  }

  void loadMore() {
    if (!state.hasMore || state.isLoading) return;
    loadProducts();
  }
}

final shopProvider = NotifierProvider<ShopNotifier, ShopState>(ShopNotifier.new);
