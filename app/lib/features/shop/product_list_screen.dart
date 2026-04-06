import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_typography.dart';
import '../../models/product.dart';
import 'similar_provider.dart';

/// Displays similar product search results with filters and sorting.
class ProductListScreen extends ConsumerStatefulWidget {
  final String category;
  final String color;
  final String style;
  final String? excludeProductId;

  const ProductListScreen({
    super.key,
    required this.category,
    required this.color,
    required this.style,
    this.excludeProductId,
  });

  @override
  ConsumerState<ProductListScreen> createState() => _ProductListScreenState();
}

class _ProductListScreenState extends ConsumerState<ProductListScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(similarProvider.notifier).search(
        category: widget.category,
        color: widget.color,
        style: widget.style,
        excludeProductId: widget.excludeProductId,
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(similarProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Similar Items'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios, size: 20),
          onPressed: () => context.pop(),
        ),
        actions: [
          if (state.brandFilter != null || state.minPrice != null)
            TextButton(
              onPressed: () => ref.read(similarProvider.notifier).clearFilters(),
              child: Text('Clear', style: TextStyle(color: AppColors.accent)),
            ),
        ],
      ),
      body: Column(
        children: [
          // Source item info
          _buildSourceHeader(),
          // Sort + Filter bar
          _buildFilterBar(state),
          // Active filters
          if (state.brandFilter != null || state.minPrice != null)
            _buildActiveFilters(state),
          // Results
          Expanded(child: _buildResults(state)),
        ],
      ),
    );
  }

  Widget _buildSourceHeader() {
    final color = AppColors.clothingColor(widget.color);
    return Container(
      margin: const EdgeInsets.fromLTRB(16, 8, 16, 0),
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: AppColors.surfaceVariant,
        borderRadius: BorderRadius.circular(10),
      ),
      child: Row(
        children: [
          const Icon(Icons.search, size: 16, color: AppColors.textSecondary),
          const SizedBox(width: 10),
          Text(
            'Similar to ',
            style: AppTypography.bodySmall.copyWith(color: AppColors.textSecondary),
          ),
          Container(
            width: 10,
            height: 10,
            decoration: BoxDecoration(color: color, shape: BoxShape.circle),
          ),
          const SizedBox(width: 4),
          Text(
            '${widget.color} ${widget.category}',
            style: AppTypography.labelMedium.copyWith(fontWeight: FontWeight.w600),
          ),
          const Spacer(),
          Text(
            widget.style,
            style: AppTypography.labelSmall.copyWith(color: AppColors.textTertiary),
          ),
        ],
      ),
    );
  }

  Widget _buildFilterBar(SimilarState state) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 4),
      child: Row(
        children: [
          // Sort dropdown
          _SortChip(
            value: state.sortBy,
            onChanged: (v) => ref.read(similarProvider.notifier).setSort(v),
          ),
          const Spacer(),
          // Brand filter
          _FilterButton(
            icon: Icons.storefront_outlined,
            label: 'Brand',
            isActive: state.brandFilter != null,
            onTap: () => _showBrandFilter(),
          ),
          const SizedBox(width: 8),
          // Price filter
          _FilterButton(
            icon: Icons.attach_money,
            label: 'Price',
            isActive: state.minPrice != null || state.maxPrice != null,
            onTap: () => _showPriceFilter(),
          ),
        ],
      ),
    );
  }

  Widget _buildActiveFilters(SimilarState state) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 4, 16, 0),
      child: Wrap(
        spacing: 8,
        children: [
          if (state.brandFilter != null)
            Chip(
              label: Text(state.brandFilter!, style: AppTypography.labelSmall),
              onDeleted: () => ref.read(similarProvider.notifier).setBrandFilter(null),
              deleteIconColor: AppColors.textTertiary,
              backgroundColor: AppColors.accentLight,
              side: BorderSide.none,
              materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
              visualDensity: VisualDensity.compact,
            ),
          if (state.minPrice != null || state.maxPrice != null)
            Chip(
              label: Text(
                '\$${state.minPrice ?? 0} – \$${state.maxPrice ?? '∞'}',
                style: AppTypography.labelSmall,
              ),
              onDeleted: () => ref.read(similarProvider.notifier).setPriceRange(null, null),
              deleteIconColor: AppColors.textTertiary,
              backgroundColor: AppColors.accentLight,
              side: BorderSide.none,
              materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
              visualDensity: VisualDensity.compact,
            ),
        ],
      ),
    );
  }

  Widget _buildResults(SimilarState state) {
    if (state.isLoading) {
      return const Center(
        child: CircularProgressIndicator(strokeWidth: 2, color: AppColors.primary),
      );
    }

    if (state.error != null) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.error_outline, size: 48, color: AppColors.textTertiary),
            const SizedBox(height: 12),
            Text('Something went wrong', style: AppTypography.bodyMedium),
          ],
        ),
      );
    }

    if (state.products.isEmpty) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.search_off, size: 48, color: AppColors.textTertiary),
            const SizedBox(height: 12),
            Text('No similar items found', style: AppTypography.bodyMedium),
            const SizedBox(height: 4),
            Text(
              'Try adjusting your filters',
              style: AppTypography.bodySmall.copyWith(color: AppColors.textSecondary),
            ),
          ],
        ),
      );
    }

    return GridView.builder(
      padding: const EdgeInsets.all(16),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        childAspectRatio: 0.62,
        crossAxisSpacing: 12,
        mainAxisSpacing: 12,
      ),
      itemCount: state.products.length,
      itemBuilder: (context, index) => _ProductGridCard(product: state.products[index]),
    );
  }

  void _showBrandFilter() async {
    // Known brands from seed data
    const brands = [
      'BABATON', 'COS', 'CONVERSE', 'DENIM FORUM', 'DR. MARTENS', 'DYNAMITE',
      'FRANK AND OAK', 'GARAGE', 'H&M', 'KOTN', 'LULULEMON', 'NEW BALANCE',
      'NIKE', 'OAK + FORT', 'ROOTS', 'RW&CO', 'SIMONS', 'TNA', 'UNIQLO',
      'VANS', 'WILFRED', 'ZARA',
    ];

    final current = ref.read(similarProvider).brandFilter;

    final selected = await showModalBottomSheet<String?>(
      context: context,
      builder: (ctx) => ListView(
        shrinkWrap: true,
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Text('Filter by Brand', style: AppTypography.headingSmall),
          ),
          if (current != null)
            ListTile(
              title: const Text('Clear filter'),
              leading: const Icon(Icons.clear),
              onTap: () => Navigator.pop(ctx, '__clear__'),
            ),
          ...brands.map((b) => ListTile(
            title: Text(b, style: AppTypography.bodyMedium),
            trailing: b == current
                ? const Icon(Icons.check, color: AppColors.accent)
                : null,
            onTap: () => Navigator.pop(ctx, b),
          )),
        ],
      ),
    );

    if (selected != null) {
      ref.read(similarProvider.notifier).setBrandFilter(
        selected == '__clear__' ? null : selected,
      );
    }
  }

  void _showPriceFilter() {
    final state = ref.read(similarProvider);
    var minVal = (state.minPrice ?? 0).toDouble();
    var maxVal = (state.maxPrice ?? 350).toDouble();

    showModalBottomSheet(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setModalState) => Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Price Range (CAD)', style: AppTypography.headingSmall),
              const SizedBox(height: 20),
              RangeSlider(
                values: RangeValues(minVal, maxVal),
                min: 0,
                max: 400,
                divisions: 40,
                labels: RangeLabels('\$${minVal.toInt()}', '\$${maxVal.toInt()}'),
                activeColor: AppColors.accent,
                onChanged: (values) {
                  setModalState(() {
                    minVal = values.start;
                    maxVal = values.end;
                  });
                },
              ),
              Center(
                child: Text(
                  '\$${minVal.toInt()} – \$${maxVal.toInt()}',
                  style: AppTypography.bodyMedium,
                ),
              ),
              const SizedBox(height: 16),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: () {
                    Navigator.pop(ctx);
                    ref.read(similarProvider.notifier).setPriceRange(
                      minVal.toInt(),
                      maxVal.toInt(),
                    );
                  },
                  child: const Text('Apply'),
                ),
              ),
              const SizedBox(height: 16),
            ],
          ),
        ),
      ),
    );
  }
}

class _SortChip extends StatelessWidget {
  final String value;
  final ValueChanged<String> onChanged;

  const _SortChip({required this.value, required this.onChanged});

  String get _label => switch (value) {
    'price_asc' => 'Price ↑',
    'price_desc' => 'Price ↓',
    'newest' => 'Newest',
    _ => 'Relevance',
  };

  @override
  Widget build(BuildContext context) {
    return PopupMenuButton<String>(
      onSelected: onChanged,
      itemBuilder: (_) => [
        const PopupMenuItem(value: 'relevance', child: Text('Relevance')),
        const PopupMenuItem(value: 'price_asc', child: Text('Price: Low to High')),
        const PopupMenuItem(value: 'price_desc', child: Text('Price: High to Low')),
        const PopupMenuItem(value: 'newest', child: Text('Newest')),
      ],
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color: AppColors.surfaceMuted,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: AppColors.borderLight),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.sort, size: 14, color: AppColors.textSecondary),
            const SizedBox(width: 6),
            Text(_label, style: AppTypography.labelMedium),
          ],
        ),
      ),
    );
  }
}

class _FilterButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final bool isActive;
  final VoidCallback onTap;

  const _FilterButton({
    required this.icon,
    required this.label,
    required this.isActive,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color: isActive ? AppColors.accentLight : AppColors.surfaceMuted,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: isActive ? AppColors.accent : AppColors.borderLight,
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 14, color: isActive ? AppColors.accentDark : AppColors.textSecondary),
            const SizedBox(width: 4),
            Text(
              label,
              style: AppTypography.labelMedium.copyWith(
                color: isActive ? AppColors.accentDark : AppColors.textPrimary,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ProductGridCard extends StatelessWidget {
  final Product product;

  const _ProductGridCard({required this.product});

  @override
  Widget build(BuildContext context) {
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
                        const Icon(Icons.image_outlined, size: 28, color: AppColors.textTertiary),
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
            product.brand.toUpperCase(),
            style: AppTypography.labelSmall.copyWith(
              letterSpacing: 0.8,
              color: AppColors.textTertiary,
            ),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 2),
          // Name
          Text(
            product.name,
            style: AppTypography.bodySmall,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 2),
          // Price + Color dot
          Row(
            children: [
              Text(
                product.formattedPrice,
                style: AppTypography.labelMedium.copyWith(fontWeight: FontWeight.w700),
              ),
              const Spacer(),
              Container(
                width: 10,
                height: 10,
                decoration: BoxDecoration(
                  color: AppColors.clothingColor(product.color),
                  shape: BoxShape.circle,
                  border: Border.all(color: AppColors.border, width: 0.5),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
