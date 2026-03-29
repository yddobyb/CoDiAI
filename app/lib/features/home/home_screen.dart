import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:image_picker/image_picker.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_typography.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  Future<void> _pickImage(BuildContext context, ImageSource source) async {
    final picker = ImagePicker();
    final picked = await picker.pickImage(source: source, maxWidth: 1024);
    if (picked != null && context.mounted) {
      context.pushNamed('analysis', extra: picked.path);
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 28),
          child: Column(
            children: [
              const Spacer(flex: 3),

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
              Text(
                'Your AI Style Companion',
                style: AppTypography.accent,
              ),
              const SizedBox(height: 16),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                child: Text(
                  'Upload a clothing photo and discover\nperfect outfit combinations.',
                  style: AppTypography.bodyMedium,
                  textAlign: TextAlign.center,
                ),
              ),

              const Spacer(flex: 2),

              // ── Tip ──
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
                decoration: BoxDecoration(
                  color: AppColors.surfaceVariant,
                  borderRadius: BorderRadius.circular(12),
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
                onPressed: () => _pickImage(context, ImageSource.gallery),
                icon: const Icon(Icons.photo_library_outlined, size: 20),
                label: const Text('Choose from Gallery'),
              ),
              const SizedBox(height: 12),
              OutlinedButton.icon(
                onPressed: () => _pickImage(context, ImageSource.camera),
                icon: const Icon(Icons.camera_alt_outlined, size: 20),
                label: const Text('Take a Photo'),
              ),

              const Spacer(flex: 1),

              // ── Footer ──
              Text(
                'Powered by on-device AI',
                style: AppTypography.labelSmall,
              ),
              const SizedBox(height: 16),
            ],
          ),
        ),
      ),
    );
  }
}
