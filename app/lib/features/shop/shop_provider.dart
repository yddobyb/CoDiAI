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
  final String? styleFilter;
  final String sortBy;
  final String? searchQuery;
  final bool isAiSearch;

  const ShopState({
    this.products = const [],
    this.isLoading = false,
    this.hasMore = true,
    this.error,
    this.categoryFilter,
    this.colorFilter,
    this.styleFilter,
    this.sortBy = 'created_at',
    this.searchQuery,
    this.isAiSearch = false,
  });

  ShopState copyWith({
    List<Product>? products,
    bool? isLoading,
    bool? hasMore,
    String? error,
    String? categoryFilter,
    String? colorFilter,
    String? styleFilter,
    String? sortBy,
    String? searchQuery,
    bool? isAiSearch,
    bool clearCategory = false,
    bool clearColor = false,
    bool clearStyle = false,
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
      styleFilter: clearStyle ? null : (styleFilter ?? this.styleFilter),
      sortBy: sortBy ?? this.sortBy,
      searchQuery: clearSearch ? null : (searchQuery ?? this.searchQuery),
      isAiSearch: isAiSearch ?? this.isAiSearch,
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
          style: state.styleFilter,
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

  void setStyle(String? style) {
    state = state.copyWith(
      styleFilter: style,
      clearStyle: style == null,
    );
    loadProducts(refresh: true);
  }

  void setSort(String sortBy) {
    state = state.copyWith(sortBy: sortBy);
    loadProducts(refresh: true);
  }

  Future<void> search(String query) async {
    if (query.isEmpty) {
      state = state.copyWith(
        clearSearch: true,
        clearCategory: true,
        clearColor: true,
        clearStyle: true,
        isAiSearch: false,
      );
      loadProducts(refresh: true);
      return;
    }

    // Try AI parsing first (Gemma on-device)
    final llm = ref.read(llmServiceProvider);
    if (llm.isGemmaReady) {
      try {
        debugPrint('[Shop] Trying AI search for: "$query"');
        final filters = await llm.parseSearchQuery(query);
        if (filters != null && filters.isNotEmpty) {
          debugPrint('[Shop] AI parsed filters: $filters');
          state = state.copyWith(
            categoryFilter: filters['category'],
            colorFilter: filters['color'],
            styleFilter: filters['style'],
            clearCategory: filters['category'] == null,
            clearColor: filters['color'] == null,
            clearStyle: filters['style'] == null,
            clearSearch: true,
            isAiSearch: true,
          );
          loadProducts(refresh: true);
          return;
        }
      } catch (e) {
        debugPrint('[Shop] AI search failed, falling back to text: $e');
      }
    }

    // Fallback: text search
    state = state.copyWith(
      searchQuery: query,
      clearCategory: true,
      clearColor: true,
      clearStyle: true,
      isAiSearch: false,
    );
    loadProducts(refresh: true);
  }

  void loadMore() {
    if (!state.hasMore || state.isLoading) return;
    loadProducts();
  }
}

final shopProvider = NotifierProvider<ShopNotifier, ShopState>(ShopNotifier.new);
