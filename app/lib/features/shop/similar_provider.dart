import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/errors/app_exception.dart';
import '../../models/product.dart';
import '../../providers/service_providers.dart';

class SimilarState {
  final List<Product> products;
  final bool isLoading;
  final String? error;
  final String? categoryFilter;
  final String? colorFilter;
  final String? brandFilter;
  final int? minPrice;
  final int? maxPrice;
  final String sortBy; // 'relevance', 'price_asc', 'price_desc', 'newest'

  const SimilarState({
    this.products = const [],
    this.isLoading = false,
    this.error,
    this.categoryFilter,
    this.colorFilter,
    this.brandFilter,
    this.minPrice,
    this.maxPrice,
    this.sortBy = 'relevance',
  });

  SimilarState copyWith({
    List<Product>? products,
    bool? isLoading,
    String? error,
    String? categoryFilter,
    String? colorFilter,
    String? brandFilter,
    int? minPrice,
    int? maxPrice,
    String? sortBy,
    bool clearCategory = false,
    bool clearColor = false,
    bool clearBrand = false,
    bool clearPrice = false,
    bool clearError = false,
  }) {
    return SimilarState(
      products: products ?? this.products,
      isLoading: isLoading ?? this.isLoading,
      error: clearError ? null : (error ?? this.error),
      categoryFilter: clearCategory ? null : (categoryFilter ?? this.categoryFilter),
      colorFilter: clearColor ? null : (colorFilter ?? this.colorFilter),
      brandFilter: clearBrand ? null : (brandFilter ?? this.brandFilter),
      minPrice: clearPrice ? null : (minPrice ?? this.minPrice),
      maxPrice: clearPrice ? null : (maxPrice ?? this.maxPrice),
      sortBy: sortBy ?? this.sortBy,
    );
  }
}

class SimilarNotifier extends Notifier<SimilarState> {
  // Source item metadata
  String _sourceCategory = '';
  String _sourceColor = '';
  String _sourceStyle = '';
  String? _sourceProductId;

  @override
  SimilarState build() => const SimilarState();

  Future<void> search({
    required String category,
    required String color,
    required String style,
    String? excludeProductId,
  }) async {
    _sourceCategory = category;
    _sourceColor = color;
    _sourceStyle = style;
    _sourceProductId = excludeProductId;

    state = state.copyWith(isLoading: true, clearError: true);

    try {
      final service = ref.read(productServiceProvider);
      final products = await service.findSimilar(
        category: category,
        color: color,
        style: style,
        excludeId: excludeProductId,
        minPrice: state.minPrice,
        maxPrice: state.maxPrice,
        brandFilter: state.brandFilter,
      );

      final sorted = _applySorting(products);
      state = state.copyWith(products: sorted, isLoading: false);
    } on NetworkException catch (e) {
      state = state.copyWith(error: e.userMessage, isLoading: false);
    } catch (e) {
      state = state.copyWith(error: 'Something went wrong', isLoading: false);
    }
  }

  void setSort(String sortBy) {
    state = state.copyWith(sortBy: sortBy, products: _applySorting(state.products));
  }

  void setBrandFilter(String? brand) {
    state = brand == null
        ? state.copyWith(clearBrand: true)
        : state.copyWith(brandFilter: brand);
    _refetch();
  }

  void setPriceRange(int? min, int? max) {
    state = state.copyWith(
      minPrice: min ?? state.minPrice,
      maxPrice: max ?? state.maxPrice,
    );
    _refetch();
  }

  void clearFilters() {
    state = state.copyWith(
      clearBrand: true,
      clearPrice: true,
      sortBy: 'relevance',
    );
    _refetch();
  }

  void _refetch() {
    if (_sourceCategory.isNotEmpty) {
      search(
        category: _sourceCategory,
        color: _sourceColor,
        style: _sourceStyle,
        excludeProductId: _sourceProductId,
      );
    }
  }

  List<Product> _applySorting(List<Product> products) {
    final sorted = List<Product>.from(products);
    switch (state.sortBy) {
      case 'price_asc':
        sorted.sort((a, b) => a.price.compareTo(b.price));
      case 'price_desc':
        sorted.sort((a, b) => b.price.compareTo(a.price));
      case 'newest':
        sorted.sort((a, b) => b.createdAt.compareTo(a.createdAt));
      default: // 'relevance' — already sorted by similarity
        break;
    }
    return sorted;
  }
}

final similarProvider = NotifierProvider<SimilarNotifier, SimilarState>(
  SimilarNotifier.new,
);
