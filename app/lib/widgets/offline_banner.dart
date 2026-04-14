import 'package:flutter/material.dart';
import '../core/theme/app_colors.dart';
import '../core/theme/app_typography.dart';

class OfflineBanner extends StatelessWidget {
  const OfflineBanner({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(vertical: 6),
      color: AppColors.textSecondary,
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.wifi_off, size: 14, color: AppColors.textInverse),
          const SizedBox(width: 8),
          Text(
            "You're offline",
            style: AppTypography.labelSmall.copyWith(color: AppColors.textInverse),
          ),
        ],
      ),
    );
  }
}
