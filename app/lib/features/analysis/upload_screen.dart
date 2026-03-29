import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_typography.dart';
import '../../widgets/confidence_bar.dart';
import 'analysis_provider.dart';

class UploadScreen extends ConsumerStatefulWidget {
  final String imagePath;
  const UploadScreen({super.key, required this.imagePath});

  @override
  ConsumerState<UploadScreen> createState() => _UploadScreenState();
}

class _UploadScreenState extends ConsumerState<UploadScreen> {
  @override
  void initState() {
    super.initState();
    // Auto-start analysis
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(analysisProvider.notifier).loadModelAndAnalyze(widget.imagePath);
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(analysisProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Analysis'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios, size: 20),
          onPressed: () => context.pop(),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // ── Image Preview ──
            ClipRRect(
              borderRadius: BorderRadius.circular(16),
              child: AspectRatio(
                aspectRatio: 3 / 4,
                child: Image.file(
                  File(widget.imagePath),
                  fit: BoxFit.cover,
                ),
              ),
            ),
            const SizedBox(height: 24),

            // ── Status / Result ──
            _buildContent(state),
          ],
        ),
      ),
    );
  }

  Widget _buildContent(AnalysisState state) {
    return switch (state.status) {
      AnalysisStatus.idle || AnalysisStatus.loadingModel => _buildLoading('Preparing model...'),
      AnalysisStatus.analyzing => _buildLoading('Analyzing your clothing...'),
      AnalysisStatus.error => _buildError(state.errorMessage ?? 'Something went wrong'),
      AnalysisStatus.done => _buildResult(state),
    };
  }

  Widget _buildLoading(String message) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 40),
      child: Column(
        children: [
          const SizedBox(
            width: 32,
            height: 32,
            child: CircularProgressIndicator(
              strokeWidth: 2.5,
              color: AppColors.primary,
            ),
          ),
          const SizedBox(height: 16),
          Text(message, style: AppTypography.bodyMedium),
        ],
      ),
    );
  }

  Widget _buildError(String message) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.errorLight,
        borderRadius: BorderRadius.circular(14),
      ),
      child: Column(
        children: [
          const Icon(Icons.error_outline, color: AppColors.error, size: 28),
          const SizedBox(height: 12),
          Text(message, style: AppTypography.bodyMedium.copyWith(color: AppColors.error)),
          const SizedBox(height: 16),
          OutlinedButton(
            onPressed: () {
              ref.read(analysisProvider.notifier).loadModelAndAnalyze(widget.imagePath);
            },
            child: const Text('Retry'),
          ),
        ],
      ),
    );
  }

  Widget _buildResult(AnalysisState state) {
    final item = state.result;
    if (item == null) return _buildError('No result available');
    final color = AppColors.clothingColor(item.color);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // ── Detected Info ──
        Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: AppColors.surface,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: AppColors.borderLight),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Detection', style: AppTypography.labelMedium.copyWith(
                letterSpacing: 1.2,
                color: AppColors.textTertiary,
              )),
              const SizedBox(height: 16),

              // Category
              Row(
                children: [
                  Text(item.icon, style: const TextStyle(fontSize: 28)),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(item.category, style: AppTypography.headingMedium),
                        const SizedBox(height: 2),
                        Text(item.style, style: AppTypography.bodyMedium),
                      ],
                    ),
                  ),
                  // Color chip
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: color.withAlpha(25),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: color.withAlpha(80)),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Container(
                          width: 12,
                          height: 12,
                          decoration: BoxDecoration(
                            color: color,
                            shape: BoxShape.circle,
                            border: Border.all(
                              color: item.color == 'white'
                                  ? AppColors.border
                                  : Colors.transparent,
                            ),
                          ),
                        ),
                        const SizedBox(width: 8),
                        Text(item.color, style: AppTypography.labelLarge.copyWith(color: AppColors.textPrimary)),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 20),

              // Confidence
              ConfidenceBar(confidence: item.confidence),

              if (item.confidence < 0.6) ...[
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  decoration: BoxDecoration(
                    color: AppColors.warningLight,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.info_outline, size: 16, color: AppColors.warning),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          'Low confidence — results may vary',
                          style: AppTypography.bodySmall.copyWith(color: AppColors.accentDark),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ],
          ),
        ),
        const SizedBox(height: 24),

        // ── CTA ──
        ElevatedButton(
          onPressed: () => context.pushNamed('result', extra: item),
          child: const Text('Get Outfit Ideas'),
        ),
      ],
    );
  }
}
