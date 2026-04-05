import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_typography.dart';
import '../../models/product.dart';
import 'shop_provider.dart';

class ShopScreen extends ConsumerStatefulWidget {
  const ShopScreen({super.key});

  @override
  ConsumerState<ShopScreen> createState() => _ShopScreenState();
}

class _ShopScreenState extends ConsumerState<ShopScreen> {
  final _scrollController = ScrollController();
  final _searchController = TextEditingController();
  String _selectedSlot = 'All';

  static const _slotFilters = ['All', 'Tops', 'Bottoms', 'Outer', 'Shoes'];
  static const _slotToCategories = {
    'Tops': ['T-shirt', 'Shirt', 'Hoodie', 'Sweater'],
    'Bottoms': ['Pants', 'Jeans', 'Shorts', 'Skirt', 'Dress'],
    'Outer': ['Jacket', 'Coat'],
    'Shoes': ['Sneakers', 'Boots', 'Flats', 'Heels'],
  };

  @override
  void initState() {
    super.initState();
    _scrollController.addListener(_onScroll);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(shopProvider.notifier).loadProducts(refresh: true);
    });
  }

  @override
  void dispose() {
    _scrollController.dispose();
    _searchController.dispose();
    super.dispose();
  }

  void _onScroll() {
    if (_scrollController.position.pixels >=
        _scrollController.position.maxScrollExtent - 200) {
      ref.read(shopProvider.notifier).loadMore();
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(shopProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Shop')),
      body: Column(
        children: [
          _buildSearchBar(),
          _buildSlotFilters(),
          if (state.categoryFilter != null) _buildActiveFilters(state),
          Expanded(child: _buildBody(state)),
        ],
      ),
    );
  }

  Widget _buildSearchBar() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 4),
      child: TextField(
        controller: _searchController,
        style: AppTypography.bodyLarge,
        decoration: InputDecoration(
          hintText: 'Search brands, items...',
          hintStyle: AppTypography.bodyMedium,
          prefixIcon: const Icon(Icons.search, size: 20, color: AppColors.textTertiary),
          suffixIcon: _searchController.text.isNotEmpty
              ? IconButton(
                  icon: const Icon(Icons.close, size: 18),
                  onPressed: () {
                    _searchController.clear();
                    ref.read(shopProvider.notifier).search('');
                    setState(() {});
                  },
                )
              : null,
          contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: const BorderSide(color: AppColors.border),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: const BorderSide(color: AppColors.border),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: const BorderSide(color: AppColors.primary, width: 1.5),
          ),
          filled: true,
          fillColor: AppColors.surface,
        ),
        onSubmitted: (query) {
          ref.read(shopProvider.notifier).search(query);
          setState(() {});
        },
        onChanged: (_) => setState(() {}),
      ),
    );
  }

  Widget _buildSlotFilters() {
    return SizedBox(
      height: 44,
      child: ListView.separated(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
        scrollDirection: Axis.horizontal,
        itemCount: _slotFilters.length,
        separatorBuilder: (_, _) => const SizedBox(width: 8),
        itemBuilder: (context, index) {
          final filter = _slotFilters[index];
          final isSelected = _selectedSlot == filter;
          return GestureDetector(
            onTap: () {
              setState(() => _selectedSlot = filter);
              if (filter == 'All') {
                ref.read(shopProvider.notifier).setCategory(null);
              } else {
                // For slot-based filter, we clear the single category
                // and will filter locally or pick first category
                ref.read(shopProvider.notifier).setCategory(null);
                // Actually, let's reload with no category and filter in the query
                // Since Supabase doesn't support IN filter via eq, we handle it differently
                _loadSlotProducts(filter);
              }
            },
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
              decoration: BoxDecoration(
                color: isSelected ? AppColors.primary : AppColors.surface,
                borderRadius: BorderRadius.circular(20),
                border: Border.all(
                  color: isSelected ? AppColors.primary : AppColors.border,
                ),
              ),
              child: Text(
                filter,
                style: AppTypography.labelLarge.copyWith(
                  color: isSelected ? AppColors.textInverse : AppColors.textPrimary,
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  void _loadSlotProducts(String slot) {
    // Show category sub-chips for the selected slot
    // For now, just load all and let the UI filter
    ref.read(shopProvider.notifier).loadProducts(refresh: true);
  }

  Widget _buildActiveFilters(ShopState state) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      child: Row(
        children: [
          if (state.categoryFilter != null)
            _filterChip(state.categoryFilter!, () {
              ref.read(shopProvider.notifier).setCategory(null);
            }),
          if (state.colorFilter != null) ...[
            const SizedBox(width: 8),
            _filterChip(state.colorFilter!, () {
              ref.read(shopProvider.notifier).setColor(null);
            }),
          ],
        ],
      ),
    );
  }

  Widget _filterChip(String label, VoidCallback onRemove) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: AppColors.accentLight,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(label, style: AppTypography.labelMedium.copyWith(color: AppColors.accentDark)),
          const SizedBox(width: 4),
          GestureDetector(
            onTap: onRemove,
            child: const Icon(Icons.close, size: 14, color: AppColors.accentDark),
          ),
        ],
      ),
    );
  }

  Widget _buildBody(ShopState state) {
    if (state.isLoading && state.products.isEmpty) {
      return const Center(child: CircularProgressIndicator(color: AppColors.accent));
    }

    if (state.error != null && state.products.isEmpty) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.error_outline, size: 48, color: AppColors.textTertiary),
            const SizedBox(height: 12),
            Text(state.error!, style: AppTypography.bodyMedium),
            const SizedBox(height: 16),
            OutlinedButton(
              onPressed: () => ref.read(shopProvider.notifier).loadProducts(refresh: true),
              child: const Text('Retry'),
            ),
          ],
        ),
      );
    }

    if (state.products.isEmpty) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.shopping_bag_outlined, size: 64, color: AppColors.textTertiary),
            const SizedBox(height: 16),
            Text('No products found', style: AppTypography.headingMedium),
            const SizedBox(height: 8),
            Text(
              'Try adjusting your filters',
              style: AppTypography.bodyMedium.copyWith(color: AppColors.textSecondary),
            ),
          ],
        ),
      );
    }

    // Filter by slot locally
    final filtered = _filterBySlot(state.products);

    return RefreshIndicator(
      color: AppColors.accent,
      onRefresh: () => ref.read(shopProvider.notifier).loadProducts(refresh: true),
      child: GridView.builder(
        controller: _scrollController,
        padding: const EdgeInsets.all(16),
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 2,
          childAspectRatio: 0.62,
          crossAxisSpacing: 12,
          mainAxisSpacing: 16,
        ),
        itemCount: filtered.length + (state.hasMore && state.isLoading ? 1 : 0),
        itemBuilder: (context, index) {
          if (index >= filtered.length) {
            return const Center(
              child: Padding(
                padding: EdgeInsets.all(16),
                child: CircularProgressIndicator(color: AppColors.accent, strokeWidth: 2),
              ),
            );
          }
          return _ProductCard(product: filtered[index]);
        },
      ),
    );
  }

  List<Product> _filterBySlot(List<Product> products) {
    if (_selectedSlot == 'All') return products;
    final categories = _slotToCategories[_selectedSlot];
    if (categories == null) return products;
    return products.where((p) => categories.contains(p.category)).toList();
  }
}

class _ProductCard extends ConsumerWidget {
  final Product product;

  const _ProductCard({required this.product});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return GestureDetector(
      onTap: () => context.push('/product', extra: product),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Image
          Expanded(
            child: Container(
              decoration: BoxDecoration(
                color: AppColors.surfaceMuted,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppColors.borderLight),
              ),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(12),
                child: Image.network(
                  product.imageUrl,
                  fit: BoxFit.cover,
                  width: double.infinity,
                  errorBuilder: (_, _, _) => Center(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(Icons.image_outlined, size: 32, color: AppColors.textTertiary),
                        const SizedBox(height: 4),
                        Text(product.category, style: AppTypography.labelSmall),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
          const SizedBox(height: 8),
          // Brand
          Text(
            product.brand,
            style: AppTypography.labelSmall.copyWith(
              color: AppColors.textTertiary,
              letterSpacing: 1.0,
            ),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 2),
          // Name
          Text(
            product.name,
            style: AppTypography.bodyMedium.copyWith(
              color: AppColors.textPrimary,
              height: 1.3,
            ),
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 4),
          // Price
          Text(
            product.formattedPrice,
            style: AppTypography.labelLarge.copyWith(fontWeight: FontWeight.w700),
          ),
        ],
      ),
    );
  }
}
