import 'package:flutter/material.dart';
import '../core/theme/app_colors.dart';
import '../core/theme/app_typography.dart';
import '../models/outfit_recommendation.dart';
import 'color_palette.dart';

class OutfitCard extends StatelessWidget {
  final OutfitRecommendation recommendation;
  final int rank;
  final bool llmLoading;

  const OutfitCard({
    super.key,
    required this.recommendation,
    required this.rank,
    this.llmLoading = false,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.borderLight),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // ── Header ──
          Padding(
            padding: const EdgeInsets.fromLTRB(18, 18, 18, 14),
            child: Row(
              children: [
                _RankBadge(rank: rank),
                const SizedBox(width: 12),
                Expanded(
                  child: Text('Look #$rank', style: AppTypography.headingSmall),
                ),
                _ScoreBadge(score: recommendation.matchScore),
              ],
            ),
          ),
          const Divider(height: 1),

          // ── Items List ──
          Padding(
            padding: const EdgeInsets.fromLTRB(18, 14, 18, 0),
            child: Column(
              children: recommendation.allItems.map((item) {
                final isUser = item.imagePath != null;
                final color = AppColors.clothingColor(item.color);
                return Padding(
                  padding: const EdgeInsets.only(bottom: 10),
                  child: Row(
                    children: [
                      Text(item.icon, style: const TextStyle(fontSize: 20)),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(item.category, style: AppTypography.labelLarge),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: color.withAlpha(20),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Container(
                              width: 8,
                              height: 8,
                              decoration: BoxDecoration(color: color, shape: BoxShape.circle),
                            ),
                            const SizedBox(width: 6),
                            Text(
                              item.color,
                              style: AppTypography.bodySmall.copyWith(color: AppColors.textSecondary),
                            ),
                          ],
                        ),
                      ),
                      if (isUser) ...[
                        const SizedBox(width: 8),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                          decoration: BoxDecoration(
                            color: AppColors.accent.withAlpha(25),
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Text(
                            'yours',
                            style: AppTypography.labelSmall.copyWith(color: AppColors.accentDark),
                          ),
                        ),
                      ],
                    ],
                  ),
                );
              }).toList(),
            ),
          ),

          // ── Color Palette ──
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 18),
            child: ColorPalette(items: recommendation.allItems),
          ),
          const SizedBox(height: 14),

          // ── Harmony & Style ──
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 18),
            child: Row(
              children: [
                Expanded(child: _InfoChip(label: recommendation.colorHarmony)),
                const SizedBox(width: 8),
                Expanded(child: _InfoChip(label: recommendation.styleConsistency)),
              ],
            ),
          ),
          const SizedBox(height: 12),

          // ── Match Reason ──
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 18),
            child: Text(
              recommendation.matchReason,
              style: AppTypography.accent.copyWith(fontSize: 14),
            ),
          ),

          // ── AI Style Tip ──
          if (recommendation.llmDescription != null) ...[
            const SizedBox(height: 14),
            Container(
              margin: const EdgeInsets.symmetric(horizontal: 18),
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: AppColors.surfaceVariant,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Icon(Icons.auto_awesome, size: 16, color: AppColors.accent),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      recommendation.llmDescription!,
                      style: AppTypography.bodySmall.copyWith(
                        color: AppColors.textSecondary,
                        height: 1.5,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ] else if (llmLoading) ...[
            const SizedBox(height: 14),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 18),
              child: Row(
                children: [
                  const SizedBox(
                    width: 14,
                    height: 14,
                    child: CircularProgressIndicator(
                      strokeWidth: 1.5,
                      color: AppColors.textTertiary,
                    ),
                  ),
                  const SizedBox(width: 10),
                  Text('Generating style tip...', style: AppTypography.bodySmall),
                ],
              ),
            ),
          ],

          const SizedBox(height: 18),
        ],
      ),
    );
  }
}

class _RankBadge extends StatelessWidget {
  final int rank;
  const _RankBadge({required this.rank});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 28,
      height: 28,
      decoration: BoxDecoration(
        color: AppColors.primary,
        borderRadius: BorderRadius.circular(8),
      ),
      alignment: Alignment.center,
      child: Text(
        '$rank',
        style: AppTypography.labelMedium.copyWith(
          color: AppColors.textInverse,
          fontWeight: FontWeight.w700,
        ),
      ),
    );
  }
}

class _ScoreBadge extends StatelessWidget {
  final double score;
  const _ScoreBadge({required this.score});

  @override
  Widget build(BuildContext context) {
    final percent = (score * 100).round();
    final color = percent >= 80
        ? AppColors.success
        : percent >= 60
            ? AppColors.warning
            : AppColors.error;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: color.withAlpha(20),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Text(
        '$percent%',
        style: AppTypography.labelMedium.copyWith(color: color, fontWeight: FontWeight.w700),
      ),
    );
  }
}

class _InfoChip extends StatelessWidget {
  final String label;
  const _InfoChip({required this.label});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: AppColors.surfaceMuted,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(
        label,
        style: AppTypography.bodySmall.copyWith(color: AppColors.textSecondary),
        maxLines: 1,
        overflow: TextOverflow.ellipsis,
        textAlign: TextAlign.center,
      ),
    );
  }
}
