import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:image_picker/image_picker.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_typography.dart';
import '../../models/outfit_recommendation.dart';
import '../../providers/premium_provider.dart';
import '../../providers/service_providers.dart';
import '../../services/daily_outfit_service.dart';
import '../../services/usage_service.dart';
import 'daily_outfit_provider.dart';

class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      // Listen for auth state to resolve, then load daily outfit
      ref.listenManual(authStateProvider, (prev, next) {
        if (next.value?.session != null) {
          ref.read(dailyOutfitProvider.notifier).load();
        }
      }, fireImmediately: true);
    });
  }

  Future<void> _pickImage(ImageSource source) async {
    final isPremium = ref.read(premiumProvider).value ?? false;
    final usageService = ref.read(usageServiceProvider);
    final remaining = await usageService.getRemainingAnalyses(isPremium: isPremium);

    if (remaining <= 0 && mounted) {
      _showUpgradeDialog();
      return;
    }

    final picker = ImagePicker();
    final picked = await picker.pickImage(source: source, maxWidth: 1024);
    if (picked != null && mounted) {
      context.pushNamed('analysis', extra: picked.path);
    }
  }

  void _showUpgradeDialog() {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Daily Limit Reached'),
        content: Text(
          'You\'ve used all ${UsageService.freeAnalysisLimit} free analyses today.\nUpgrade to Premium for unlimited analyses.',
          style: AppTypography.bodyMedium,
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Maybe Later'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(ctx);
              context.push('/premium');
            },
            child: const Text('Upgrade'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final dailyState = ref.watch(dailyOutfitProvider);

    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24),
          child: Column(
            children: [
              SizedBox(height: MediaQuery.of(context).size.height * 0.06),

              // ── Brand Mark ──
              Container(
                width: 64,
                height: 64,
                decoration: BoxDecoration(
                  color: AppColors.primary,
                  borderRadius: BorderRadius.circular(16),
                ),
                child: const Icon(
                  Icons.auto_awesome,
                  color: AppColors.textInverse,
                  size: 28,
                ),
              ),
              const SizedBox(height: 24),

              // ── Title ──
              Text('CoDi', style: AppTypography.displayLarge),
              const SizedBox(height: 8),
              Text('Your AI Style Companion', style: AppTypography.accent),
              const SizedBox(height: 16),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                child: Text(
                  'Upload a clothing photo and discover\nperfect outfit combinations.',
                  style: AppTypography.bodyMedium,
                  textAlign: TextAlign.center,
                ),
              ),
              const SizedBox(height: 28),

              // ── Today's Outfit ──
              if (dailyState.outfit != null) ...[
                _DailyOutfitCard(outfit: dailyState.outfit!),
                const SizedBox(height: 20),
              ] else if (dailyState.isLoading) ...[
                _buildDailyLoading(),
                const SizedBox(height: 20),
              ],

              // ── Tip ──
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
                decoration: BoxDecoration(
                  color: AppColors.surfaceVariant,
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.lightbulb_outline, size: 18, color: AppColors.accentDark),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        'For best results, use a close-up of a single item',
                        style: AppTypography.bodySmall.copyWith(color: AppColors.textSecondary),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),

              // ── Actions ──
              ElevatedButton.icon(
                onPressed: () => _pickImage(ImageSource.gallery),
                icon: const Icon(Icons.photo_library_outlined, size: 20),
                label: const Text('Choose from Gallery'),
              ),
              const SizedBox(height: 12),
              OutlinedButton.icon(
                onPressed: () => _pickImage(ImageSource.camera),
                icon: const Icon(Icons.camera_alt_outlined, size: 20),
                label: const Text('Take a Photo'),
              ),
              const SizedBox(height: 24),

              // ── Footer ──
              Text('Powered by on-device AI', style: AppTypography.labelSmall),
              const SizedBox(height: 16),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDailyLoading() {
    return Container(
      height: 80,
      decoration: BoxDecoration(
        color: AppColors.surfaceVariant,
        borderRadius: BorderRadius.circular(16),
      ),
      child: const Center(
        child: SizedBox(
          width: 16, height: 16,
          child: CircularProgressIndicator(strokeWidth: 1.5, color: AppColors.textTertiary),
        ),
      ),
    );
  }
}

class _DailyOutfitCard extends StatelessWidget {
  final OutfitRecommendation outfit;

  const _DailyOutfitCard({required this.outfit});

  @override
  Widget build(BuildContext context) {
    final season = DailyOutfitService.currentSeason;
    final seasonIcon = switch (season) {
      'spring' => '🌸',
      'summer' => '☀️',
      'fall' => '🍂',
      'winter' => '❄️',
      _ => '👗',
    };

    return GestureDetector(
      onTap: () => context.push('/result', extra: outfit.userItem),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [
              AppColors.surfaceVariant,
              AppColors.accentLight.withAlpha(80),
            ],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: AppColors.accent.withAlpha(60)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Row(
              children: [
                Text(seasonIcon, style: const TextStyle(fontSize: 18)),
                const SizedBox(width: 8),
                Text("Today's Outfit", style: AppTypography.headingSmall),
                const Spacer(),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                    color: AppColors.accent.withAlpha(30),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    '${outfit.matchPercent}% match',
                    style: AppTypography.labelSmall.copyWith(color: AppColors.accentDark),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),

            // Items row
            Row(
              children: outfit.allItems.map((item) {
                return Expanded(
                  child: Column(
                    children: [
                      Text(item.icon, style: const TextStyle(fontSize: 22)),
                      const SizedBox(height: 4),
                      Text(
                        item.category,
                        style: AppTypography.labelSmall,
                        textAlign: TextAlign.center,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 2),
                      Container(
                        width: 10, height: 10,
                        decoration: BoxDecoration(
                          color: AppColors.clothingColor(item.color),
                          shape: BoxShape.circle,
                          border: Border.all(
                            color: item.color == 'white' ? AppColors.border : Colors.transparent,
                          ),
                        ),
                      ),
                    ],
                  ),
                );
              }).toList(),
            ),
            const SizedBox(height: 10),

            // Tap hint
            Center(
              child: Text(
                'Tap to see full outfit details',
                style: AppTypography.labelSmall.copyWith(color: AppColors.textTertiary),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
