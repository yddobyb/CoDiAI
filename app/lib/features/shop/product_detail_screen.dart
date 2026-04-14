import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_typography.dart';
import '../../models/clothing_item.dart';
import '../../models/product.dart';
import '../../providers/service_providers.dart';
import '../../widgets/cached_product_image.dart';

class ProductDetailScreen extends ConsumerWidget {
  final Product product;

  const ProductDetailScreen({super.key, required this.product});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      body: CustomScrollView(
        slivers: [
          _buildAppBar(context),
          SliverToBoxAdapter(child: _buildInfo()),
          SliverToBoxAdapter(child: _buildTags(context)),
          const SliverToBoxAdapter(child: SizedBox(height: 120)),
        ],
      ),
      bottomSheet: _buildBottomBar(context, ref),
    );
  }

  Widget _buildAppBar(BuildContext context) {
    return SliverAppBar(
      expandedHeight: MediaQuery.of(context).size.height * 0.45,
      pinned: true,
      backgroundColor: AppColors.surface,
      leading: IconButton(
        icon: const Icon(Icons.arrow_back_ios, size: 20),
        onPressed: () => context.pop(),
      ),
      flexibleSpace: FlexibleSpaceBar(
        background: CachedProductImage(
          imageUrl: product.imageUrl,
          category: product.category,
          borderRadius: 0,
        ),
      ),
    );
  }

  Widget _buildInfo() {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Brand
          Text(
            product.brand.toUpperCase(),
            style: AppTypography.labelMedium.copyWith(
              letterSpacing: 1.5,
              color: AppColors.textTertiary,
            ),
          ),
          const SizedBox(height: 6),
          // Name
          Text(product.name, style: AppTypography.headingLarge),
          const SizedBox(height: 12),
          // Price
          Text(
            product.formattedPrice,
            style: AppTypography.displaySmall.copyWith(fontWeight: FontWeight.w700),
          ),
        ],
      ),
    );
  }

  Widget _buildTags(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Divider(color: AppColors.borderLight),
          const SizedBox(height: 12),
          Text('Details', style: AppTypography.headingSmall),
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              _tag(Icons.category_outlined, product.category),
              _colorTag(product.color),
              _tag(Icons.style_outlined, product.style),
              _tag(Icons.label_outlined, product.slotLabel),
            ],
          ),
          const SizedBox(height: 20),
          // Find Similar button
          SizedBox(
            width: double.infinity,
            child: OutlinedButton.icon(
              onPressed: () => context.push('/similar', extra: {
                'category': product.category,
                'color': product.color,
                'style': product.style,
                'excludeId': product.id,
              }),
              icon: const Icon(Icons.search, size: 18),
              label: const Text('Find Similar Items'),
              style: OutlinedButton.styleFrom(
                minimumSize: const Size(0, 44),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
            ),
          ),
          const SizedBox(height: 20),
        ],
      ),
    );
  }

  Widget _tag(IconData icon, String label) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: AppColors.surfaceMuted,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppColors.borderLight),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14, color: AppColors.textSecondary),
          const SizedBox(width: 6),
          Text(label, style: AppTypography.labelMedium),
        ],
      ),
    );
  }

  Widget _colorTag(String color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: AppColors.surfaceMuted,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppColors.borderLight),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 12,
            height: 12,
            decoration: BoxDecoration(
              color: AppColors.clothingColor(color),
              shape: BoxShape.circle,
              border: Border.all(color: AppColors.border, width: 0.5),
            ),
          ),
          const SizedBox(width: 6),
          Text(color, style: AppTypography.labelMedium),
        ],
      ),
    );
  }

  Widget _buildBottomBar(BuildContext context, WidgetRef ref) {
    return Container(
      padding: const EdgeInsets.fromLTRB(24, 12, 24, 32),
      decoration: const BoxDecoration(
        color: AppColors.surface,
        border: Border(top: BorderSide(color: AppColors.borderLight)),
      ),
      child: Row(
        children: [
          // Outfit recommendation button
          Expanded(
            child: OutlinedButton.icon(
              onPressed: () {
                final item = ClothingItem(
                  category: product.category,
                  color: product.color,
                  style: product.style,
                  confidence: 1.0,
                  imagePath: product.imageUrl,
                );
                context.push('/result', extra: item);
              },
              icon: const Icon(Icons.auto_awesome, size: 18),
              label: const Text('Get Outfit'),
              style: OutlinedButton.styleFrom(
                minimumSize: const Size(0, 48),
                foregroundColor: AppColors.primary,
                side: const BorderSide(color: AppColors.primary),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
            ),
          ),
          const SizedBox(width: 12),
          // Buy button
          Expanded(
            flex: 2,
            child: ElevatedButton.icon(
              onPressed: product.affiliateUrl != null
                  ? () {
                      ref.read(clickTrackingServiceProvider).trackClick(
                        productId: product.id,
                      );
                      _openLink(product.affiliateUrl!);
                    }
                  : null,
              icon: const Icon(Icons.open_in_new, size: 18),
              label: Text(product.affiliateUrl != null ? 'Buy Now' : 'Coming Soon'),
              style: ElevatedButton.styleFrom(
                minimumSize: const Size(0, 48),
                backgroundColor: AppColors.primary,
                foregroundColor: AppColors.textInverse,
                disabledBackgroundColor: AppColors.surfaceVariant,
                disabledForegroundColor: AppColors.textTertiary,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _openLink(String url) async {
    final uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    }
  }
}
