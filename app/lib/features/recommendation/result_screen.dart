import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_typography.dart';
import '../../models/clothing_item.dart';
import '../../providers/premium_provider.dart';
import '../../widgets/outfit_card.dart';
import '../../widgets/product_suggestion_row.dart';
import 'recommendation_provider.dart';

class ResultScreen extends ConsumerStatefulWidget {
  final ClothingItem clothingItem;
  const ResultScreen({super.key, required this.clothingItem});

  @override
  ConsumerState<ResultScreen> createState() => _ResultScreenState();
}

class _ResultScreenState extends ConsumerState<ResultScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(recommendationProvider.notifier).generate(widget.clothingItem);
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(recommendationProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Outfit Ideas'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios, size: 20),
          onPressed: () => context.pop(),
        ),
      ),
      body: state.isLoading
          ? const Center(
              child: CircularProgressIndicator(
                strokeWidth: 2,
                color: AppColors.primary,
              ),
            )
          : ListView(
              padding: const EdgeInsets.fromLTRB(24, 8, 24, 32),
              children: [
                // ── Your Item Summary ──
                _buildUserItemCard(),
                const SizedBox(height: 28),

                // ── Section Header ──
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        'Recommended Outfits',
                        style: AppTypography.headingMedium,
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: AppColors.surfaceVariant,
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Text(
                        '${state.recommendations.length} looks',
                        style: AppTypography.labelMedium,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),

                // ── Outfit Cards + Product Suggestions ──
                ...List.generate(state.recommendations.length, (i) {
                  final rec = state.recommendations[i];
                  return Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      OutfitCard(
                        recommendation: rec,
                        rank: i + 1,
                        llmLoading: state.llmLoading,
                      ),
                      // Product suggestions for each recommended (non-user) item
                      ...rec.recommendedItems.map((item) => Padding(
                        padding: const EdgeInsets.only(top: 12),
                        child: ProductSuggestionRow(item: item),
                      )),
                      const SizedBox(height: 16),
                    ],
                  );
                }),

                // ── Promoted Brands ──
                _buildPromotedBrands(),
                const SizedBox(height: 16),

                // ── Try Another ──
                OutlinedButton.icon(
                  onPressed: () => context.go('/'),
                  icon: const Icon(Icons.refresh, size: 18),
                  label: const Text('Try Another Item'),
                ),
              ],
            ),
    );
  }

  Widget _buildPromotedBrands() {
    final isPremium = ref.watch(premiumProvider).value ?? false;
    if (isPremium) return const SizedBox.shrink();

    const brands = [
      {'name': 'Aritzia', 'tagline': 'Everyday luxury'},
      {'name': 'Garage', 'tagline': 'Trendy & affordable'},
      {'name': 'Oak + Fort', 'tagline': 'Minimal aesthetic'},
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            const Icon(Icons.local_offer_outlined, size: 14, color: AppColors.textTertiary),
            const SizedBox(width: 6),
            Text(
              'Featured Brands',
              style: AppTypography.labelMedium.copyWith(color: AppColors.textTertiary),
            ),
          ],
        ),
        const SizedBox(height: 10),
        SizedBox(
          height: 72,
          child: ListView.separated(
            scrollDirection: Axis.horizontal,
            itemCount: brands.length,
            separatorBuilder: (_, _) => const SizedBox(width: 10),
            itemBuilder: (context, index) {
              final brand = brands[index];
              return GestureDetector(
                onTap: () => context.go('/shop'),
                child: Container(
                  width: 150,
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: AppColors.surfaceMuted,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: AppColors.borderLight),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        brand['name']!,
                        style: AppTypography.labelMedium.copyWith(fontWeight: FontWeight.w700),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        brand['tagline']!,
                        style: AppTypography.labelSmall,
                      ),
                    ],
                  ),
                ),
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _buildUserItemCard() {
    final item = widget.clothingItem;
    final color = AppColors.clothingColor(item.color);

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.surfaceVariant,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        children: [
          Text(item.icon, style: const TextStyle(fontSize: 24)),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '${item.color} ${item.category}',
                  style: AppTypography.headingSmall,
                ),
                const SizedBox(height: 2),
                Text(item.style, style: AppTypography.bodySmall),
              ],
            ),
          ),
          Container(
            width: 12,
            height: 12,
            decoration: BoxDecoration(
              color: color,
              shape: BoxShape.circle,
              border: Border.all(
                color: item.color == 'white' ? AppColors.border : Colors.transparent,
                width: 1.5,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
