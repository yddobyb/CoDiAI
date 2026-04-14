import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:shimmer/shimmer.dart';
import '../core/theme/app_colors.dart';
import '../core/theme/app_typography.dart';

/// Cached network image with shimmer placeholder and styled error fallback.
class CachedProductImage extends StatelessWidget {
  final String imageUrl;
  final double borderRadius;
  final String? category;
  final BoxFit fit;

  const CachedProductImage({
    super.key,
    required this.imageUrl,
    this.borderRadius = 12,
    this.category,
    this.fit = BoxFit.cover,
  });

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(borderRadius),
      child: CachedNetworkImage(
        imageUrl: imageUrl,
        fit: fit,
        width: double.infinity,
        placeholder: (context, url) => Shimmer.fromColors(
          baseColor: AppColors.surfaceVariant,
          highlightColor: AppColors.surface,
          child: Container(color: AppColors.surfaceVariant),
        ),
        errorWidget: (context, url, error) => Container(
          color: AppColors.surfaceMuted,
          child: Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.image_outlined, size: 32, color: AppColors.textTertiary),
                if (category != null) ...[
                  const SizedBox(height: 4),
                  Text(category!, style: AppTypography.labelSmall),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}
