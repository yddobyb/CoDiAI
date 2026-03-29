import 'package:flutter/material.dart';
import '../core/theme/app_colors.dart';
import '../core/theme/app_typography.dart';

class ConfidenceBar extends StatelessWidget {
  final double confidence;
  const ConfidenceBar({super.key, required this.confidence});

  @override
  Widget build(BuildContext context) {
    final percent = (confidence * 100).round();
    final color = confidence >= 0.8
        ? AppColors.success
        : confidence >= 0.6
            ? AppColors.warning
            : AppColors.error;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'CONFIDENCE',
              style: AppTypography.labelSmall.copyWith(letterSpacing: 1.2),
            ),
            Text(
              '$percent%',
              style: AppTypography.labelMedium.copyWith(
                color: color,
                fontWeight: FontWeight.w700,
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        ClipRRect(
          borderRadius: BorderRadius.circular(4),
          child: LinearProgressIndicator(
            value: confidence,
            minHeight: 6,
            backgroundColor: AppColors.surfaceVariant,
            valueColor: AlwaysStoppedAnimation<Color>(color),
          ),
        ),
      ],
    );
  }
}
