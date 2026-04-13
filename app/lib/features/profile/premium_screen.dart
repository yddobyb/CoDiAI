import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_typography.dart';
import '../../services/usage_service.dart';

class PremiumScreen extends ConsumerWidget {
  const PremiumScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Premium'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios, size: 20),
          onPressed: () => context.pop(),
        ),
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(24, 16, 24, 40),
        children: [
          // Hero
          Center(
            child: Container(
              width: 64,
              height: 64,
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [AppColors.accent, Color(0xFFD4A574)],
                ),
                borderRadius: BorderRadius.circular(16),
              ),
              child: const Icon(Icons.auto_awesome, color: AppColors.textInverse, size: 28),
            ),
          ),
          const SizedBox(height: 20),
          Text(
            'CoDi Premium',
            style: AppTypography.displaySmall,
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 8),
          Text(
            'Unlock the full styling experience',
            style: AppTypography.bodyMedium.copyWith(color: AppColors.textSecondary),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 32),

          // Plan comparison
          _PlanCard(
            title: 'Free',
            price: '\$0',
            features: [
              '${UsageService.freeAnalysisLimit} analyses per day',
              'Basic outfit recommendations',
              'Shop browsing',
            ],
            limitations: [
              'Limited daily analyses',
              'Ads included',
            ],
            isCurrent: true,
          ),
          const SizedBox(height: 16),
          _PlanCard(
            title: 'Premium',
            price: '\$4.99/mo',
            features: [
              'Unlimited analyses',
              'Advanced outfit recommendations',
              'Similar product search',
              'Style reports',
              'Ad-free experience',
              'Priority support',
            ],
            limitations: [],
            isPremium: true,
          ),
          const SizedBox(height: 24),

          // CTA
          ElevatedButton(
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Premium subscriptions coming soon!'),
                  behavior: SnackBarBehavior.floating,
                ),
              );
            },
            style: ElevatedButton.styleFrom(
              minimumSize: const Size(double.infinity, 52),
              backgroundColor: AppColors.accent,
              foregroundColor: AppColors.textInverse,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
            ),
            child: const Text('Start Free Trial'),
          ),
          const SizedBox(height: 12),
          Text(
            '7-day free trial, then \$4.99/month.\nCancel anytime.',
            style: AppTypography.bodySmall.copyWith(color: AppColors.textTertiary),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}

class _PlanCard extends StatelessWidget {
  final String title;
  final String price;
  final List<String> features;
  final List<String> limitations;
  final bool isCurrent;
  final bool isPremium;

  const _PlanCard({
    required this.title,
    required this.price,
    required this.features,
    this.limitations = const [],
    this.isCurrent = false,
    this.isPremium = false,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: isPremium ? AppColors.primary : AppColors.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: isPremium ? AppColors.accent : AppColors.borderLight,
          width: isPremium ? 2 : 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(
                title,
                style: AppTypography.headingMedium.copyWith(
                  color: isPremium ? AppColors.textInverse : AppColors.textPrimary,
                ),
              ),
              const Spacer(),
              Text(
                price,
                style: AppTypography.headingSmall.copyWith(
                  color: isPremium ? AppColors.accent : AppColors.textSecondary,
                ),
              ),
            ],
          ),
          if (isCurrent) ...[
            const SizedBox(height: 4),
            Text(
              'Current plan',
              style: AppTypography.labelSmall.copyWith(color: AppColors.textTertiary),
            ),
          ],
          const SizedBox(height: 16),
          ...features.map((f) => Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Row(
              children: [
                Icon(
                  Icons.check_circle,
                  size: 16,
                  color: isPremium ? AppColors.accent : AppColors.success,
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    f,
                    style: AppTypography.bodySmall.copyWith(
                      color: isPremium ? AppColors.textInverse : AppColors.textPrimary,
                    ),
                  ),
                ),
              ],
            ),
          )),
          ...limitations.map((l) => Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Row(
              children: [
                const Icon(Icons.remove_circle_outline, size: 16, color: AppColors.textTertiary),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    l,
                    style: AppTypography.bodySmall.copyWith(color: AppColors.textTertiary),
                  ),
                ),
              ],
            ),
          )),
        ],
      ),
    );
  }
}
