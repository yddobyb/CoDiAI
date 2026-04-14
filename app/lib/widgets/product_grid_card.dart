import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../core/theme/app_colors.dart';
import '../core/theme/app_typography.dart';
import '../models/product.dart';
import 'cached_product_image.dart';

/// Unified product grid card used in Shop and Similar Items screens.
class ProductGridCard extends StatelessWidget {
  final Product product;

  const ProductGridCard({super.key, required this.product});

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
              child: CachedProductImage(
                imageUrl: product.imageUrl,
                category: product.category,
              ),
            ),
          ),
          const SizedBox(height: 8),
          // Brand
          Text(
            product.brand.toUpperCase(),
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
            style: AppTypography.bodySmall.copyWith(
              color: AppColors.textPrimary,
              height: 1.3,
            ),
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 4),
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
