import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../core/theme/app_colors.dart';
import '../core/theme/app_typography.dart';
import '../models/clothing_item.dart';
import '../models/product.dart';
import '../providers/service_providers.dart';

/// Horizontal scrollable row of products matching a recommended clothing item.
class ProductSuggestionRow extends ConsumerStatefulWidget {
  final ClothingItem item;

  const ProductSuggestionRow({super.key, required this.item});

  @override
  ConsumerState<ProductSuggestionRow> createState() => _ProductSuggestionRowState();
}

class _ProductSuggestionRowState extends ConsumerState<ProductSuggestionRow> {
  List<Product>? _products;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _fetchProducts();
  }

  Future<void> _fetchProducts() async {
    try {
      final service = ref.read(productServiceProvider);
      final products = await service.fetchMatchingProducts(
        category: widget.item.category,
        color: widget.item.color,
        limit: 6,
      );
      if (mounted) {
        setState(() {
          _products = products;
          _loading = false;
        });
      }
    } catch (_) {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const SizedBox(
        height: 48,
        child: Center(
          child: SizedBox(
            width: 16,
            height: 16,
            child: CircularProgressIndicator(strokeWidth: 1.5, color: AppColors.textTertiary),
          ),
        ),
      );
    }

    if (_products == null || _products!.isEmpty) return const SizedBox.shrink();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Header
        Padding(
          padding: const EdgeInsets.only(bottom: 8),
          child: Row(
            children: [
              const Icon(Icons.shopping_bag_outlined, size: 14, color: AppColors.accent),
              const SizedBox(width: 6),
              Text(
                'Shop ${widget.item.color} ${widget.item.category}',
                style: AppTypography.labelMedium.copyWith(color: AppColors.accentDark),
              ),
              const Spacer(),
              Text(
                '${_products!.length} items',
                style: AppTypography.bodySmall,
              ),
            ],
          ),
        ),
        // Horizontal product list
        SizedBox(
          height: 150,
          child: ListView.separated(
            scrollDirection: Axis.horizontal,
            itemCount: _products!.length,
            separatorBuilder: (_, _) => const SizedBox(width: 10),
            itemBuilder: (context, index) => _MiniProductCard(product: _products![index]),
          ),
        ),
      ],
    );
  }
}

class _MiniProductCard extends StatelessWidget {
  final Product product;

  const _MiniProductCard({required this.product});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => context.push('/product', extra: product),
      child: SizedBox(
        width: 110,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Image
            Expanded(
              child: Container(
                width: 110,
                decoration: BoxDecoration(
                  color: AppColors.surfaceMuted,
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: AppColors.borderLight),
                ),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(10),
                  child: Image.network(
                    product.imageUrl,
                    fit: BoxFit.cover,
                    errorBuilder: (_, _, _) => Center(
                      child: Text(product.category, style: AppTypography.labelSmall),
                    ),
                  ),
                ),
              ),
            ),
            const SizedBox(height: 6),
            // Brand
            Text(
              product.brand,
              style: AppTypography.labelSmall.copyWith(letterSpacing: 0.5),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
            // Price
            Text(
              product.formattedPrice,
              style: AppTypography.labelMedium.copyWith(fontWeight: FontWeight.w700),
            ),
          ],
        ),
      ),
    );
  }
}
