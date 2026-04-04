import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_typography.dart';
import '../../providers/service_providers.dart';
import '../../services/history_service.dart';
import 'history_provider.dart';

class HistoryScreen extends ConsumerStatefulWidget {
  const HistoryScreen({super.key});

  @override
  ConsumerState<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends ConsumerState<HistoryScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final authState = ref.read(authStateProvider);
      if (authState.value?.session != null) {
        ref.read(historyProvider.notifier).loadHistory();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final auth = ref.watch(authStateProvider);
    final isLoggedIn = auth.value?.session != null;

    return Scaffold(
      appBar: AppBar(title: const Text('History')),
      body: isLoggedIn ? _buildHistory() : _buildLoginPrompt(),
    );
  }

  Widget _buildLoginPrompt() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.history, size: 64, color: AppColors.textTertiary),
            const SizedBox(height: 20),
            Text('Outfit History', style: AppTypography.headingMedium),
            const SizedBox(height: 8),
            Text(
              'Sign in to view your outfit recommendations',
              style: AppTypography.bodyMedium.copyWith(color: AppColors.textSecondary),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: () => context.push('/auth'),
              child: const Text('Sign In'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHistory() {
    final state = ref.watch(historyProvider);

    if (state.isLoading) {
      return const Center(
        child: CircularProgressIndicator(strokeWidth: 2, color: AppColors.primary),
      );
    }

    if (state.entries.isEmpty) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.style_outlined, size: 48, color: AppColors.textTertiary),
            const SizedBox(height: 12),
            Text('No history yet', style: AppTypography.bodyMedium.copyWith(color: AppColors.textSecondary)),
            const SizedBox(height: 4),
            Text(
              'Your outfit recommendations will appear here',
              style: AppTypography.bodySmall.copyWith(color: AppColors.textTertiary),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: () => ref.read(historyProvider.notifier).loadHistory(),
      child: ListView.separated(
        padding: const EdgeInsets.fromLTRB(20, 12, 20, 32),
        itemCount: state.entries.length,
        separatorBuilder: (_, index) => const SizedBox(height: 12),
        itemBuilder: (context, i) => _HistoryCard(
          entry: state.entries[i],
          onTap: () => _viewDetail(state.entries[i]),
          onLike: () => ref.read(historyProvider.notifier).toggleLiked(state.entries[i].id, true),
          onDislike: () => ref.read(historyProvider.notifier).toggleLiked(state.entries[i].id, false),
        ),
      ),
    );
  }

  void _viewDetail(HistoryEntry entry) {
    context.pushNamed('result', extra: entry.userItem);
  }
}

class _HistoryCard extends StatelessWidget {
  final HistoryEntry entry;
  final VoidCallback onTap;
  final VoidCallback onLike;
  final VoidCallback onDislike;

  const _HistoryCard({
    required this.entry,
    required this.onTap,
    required this.onLike,
    required this.onDislike,
  });

  @override
  Widget build(BuildContext context) {
    final userItem = entry.userItem;
    final color = AppColors.clothingColor(userItem.color);
    final timeAgo = _formatTimeAgo(entry.createdAt);
    final recCount = entry.recommendations.length;

    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: AppColors.borderLight),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Top row: item info + time
            Row(
              children: [
                Text(userItem.icon, style: const TextStyle(fontSize: 24)),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '${userItem.color} ${userItem.category}',
                        style: AppTypography.headingSmall,
                      ),
                      Text(
                        '$recCount outfit ideas',
                        style: AppTypography.bodySmall.copyWith(color: AppColors.textSecondary),
                      ),
                    ],
                  ),
                ),
                Container(
                  width: 16, height: 16,
                  decoration: BoxDecoration(
                    color: color,
                    shape: BoxShape.circle,
                    border: Border.all(
                      color: userItem.color == 'white' ? AppColors.border : Colors.transparent,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),

            // Recommendation preview
            if (entry.recommendations.isNotEmpty)
              Wrap(
                spacing: 6,
                runSpacing: 4,
                children: entry.recommendations.first.recommendedItems.map((item) {
                  return Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: AppColors.surfaceVariant,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      '${item.icon} ${item.color} ${item.category}',
                      style: AppTypography.labelSmall,
                    ),
                  );
                }).toList(),
              ),
            const SizedBox(height: 12),

            // Bottom row: time + like/dislike
            Row(
              children: [
                Icon(Icons.access_time, size: 14, color: AppColors.textTertiary),
                const SizedBox(width: 4),
                Text(timeAgo, style: AppTypography.bodySmall.copyWith(color: AppColors.textTertiary)),
                const Spacer(),
                _LikeButton(
                  icon: Icons.thumb_up_outlined,
                  activeIcon: Icons.thumb_up,
                  isActive: entry.liked == true,
                  onTap: onLike,
                ),
                const SizedBox(width: 12),
                _LikeButton(
                  icon: Icons.thumb_down_outlined,
                  activeIcon: Icons.thumb_down,
                  isActive: entry.liked == false,
                  onTap: onDislike,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  String _formatTimeAgo(DateTime dateTime) {
    final diff = DateTime.now().difference(dateTime);
    if (diff.inMinutes < 1) return 'Just now';
    if (diff.inMinutes < 60) return '${diff.inMinutes}m ago';
    if (diff.inHours < 24) return '${diff.inHours}h ago';
    if (diff.inDays < 7) return '${diff.inDays}d ago';
    return '${dateTime.month}/${dateTime.day}';
  }
}

class _LikeButton extends StatelessWidget {
  final IconData icon;
  final IconData activeIcon;
  final bool isActive;
  final VoidCallback onTap;

  const _LikeButton({
    required this.icon,
    required this.activeIcon,
    required this.isActive,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Icon(
        isActive ? activeIcon : icon,
        size: 20,
        color: isActive ? AppColors.accent : AppColors.textTertiary,
      ),
    );
  }
}
