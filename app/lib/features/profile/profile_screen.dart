import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_typography.dart';
import '../../providers/premium_provider.dart';
import '../../providers/service_providers.dart';
import '../closet/closet_provider.dart';
import 'gemma_provider.dart';

class ProfileScreen extends ConsumerStatefulWidget {
  const ProfileScreen({super.key});

  @override
  ConsumerState<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends ConsumerState<ProfileScreen> {
  Map<String, dynamic>? _profile;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _loadProfile());
  }

  Future<void> _loadProfile() async {
    final auth = ref.read(authStateProvider);
    if (auth.value?.session == null) {
      setState(() => _isLoading = false);
      return;
    }
    try {
      final profileService = ref.read(profileServiceProvider);
      final profile = await profileService.fetchProfile();
      if (mounted) {
        setState(() { _profile = profile; _isLoading = false; });
        ref.invalidate(premiumProvider); // Refresh premium status
      }
    } catch (e) {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final auth = ref.watch(authStateProvider);
    final isLoggedIn = auth.value?.session != null;

    return Scaffold(
      appBar: AppBar(title: const Text('Profile')),
      body: isLoggedIn ? _buildProfile() : _buildLoginPrompt(),
    );
  }

  Widget _buildLoginPrompt() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.person_outline, size: 64, color: AppColors.textTertiary),
            const SizedBox(height: 20),
            Text('Your Profile', style: AppTypography.headingMedium),
            const SizedBox(height: 8),
            Text(
              'Sign in to personalize your experience',
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

  Widget _buildProfile() {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator(strokeWidth: 2, color: AppColors.primary));
    }

    final email = _profile?['email'] as String? ?? '';
    final nickname = _profile?['nickname'] as String?;
    final style = _profile?['style_preference'] as String? ?? 'casual';
    final closetState = ref.watch(closetProvider);
    final itemCount = closetState.items.length;

    return ListView(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
      children: [
        // Avatar + Name
        Center(
          child: Column(
            children: [
              CircleAvatar(
                radius: 40,
                backgroundColor: AppColors.accent,
                child: Text(
                  (nickname ?? email).isNotEmpty ? (nickname ?? email)[0].toUpperCase() : '?',
                  style: AppTypography.displaySmall.copyWith(color: AppColors.surface),
                ),
              ),
              const SizedBox(height: 14),
              Text(nickname ?? 'Set your nickname', style: AppTypography.headingMedium),
              const SizedBox(height: 4),
              Text(email, style: AppTypography.bodySmall.copyWith(color: AppColors.textSecondary)),
            ],
          ),
        ),
        const SizedBox(height: 32),

        // Stats
        Container(
          padding: const EdgeInsets.all(18),
          decoration: BoxDecoration(
            color: AppColors.surfaceVariant,
            borderRadius: BorderRadius.circular(16),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _StatItem(label: 'Items', value: '$itemCount'),
              _StatItem(label: 'Style', value: style),
            ],
          ),
        ),
        const SizedBox(height: 24),

        // Premium badge
        _buildPremiumCard(),
        const SizedBox(height: 24),

        // Settings
        _SettingsTile(
          icon: Icons.person_outline,
          title: 'Edit Nickname',
          onTap: () => _editNickname(),
        ),
        _SettingsTile(
          icon: Icons.style_outlined,
          title: 'Style Preference',
          subtitle: style,
          onTap: () => _editStylePreference(),
        ),
        const SizedBox(height: 24),

        // Offline AI
        _buildOfflineAiSection(),
        const SizedBox(height: 24),

        // Logout
        OutlinedButton.icon(
          onPressed: () async {
            await ref.read(authServiceProvider).signOut();
            if (mounted) setState(() { _profile = null; _isLoading = false; });
          },
          icon: const Icon(Icons.logout, size: 18),
          label: const Text('Sign Out'),
        ),
      ],
    );
  }

  Widget _buildPremiumCard() {
    final isPremium = ref.watch(premiumProvider).value ?? false;

    if (isPremium) {
      return Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          gradient: const LinearGradient(
            colors: [AppColors.accent, Color(0xFFD4A574)],
          ),
          borderRadius: BorderRadius.circular(16),
        ),
        child: Row(
          children: [
            const Icon(Icons.auto_awesome, color: AppColors.textInverse),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Premium', style: AppTypography.headingSmall.copyWith(color: AppColors.textInverse)),
                  Text('Unlimited access', style: AppTypography.bodySmall.copyWith(color: AppColors.textInverse.withAlpha(180))),
                ],
              ),
            ),
          ],
        ),
      );
    }

    return GestureDetector(
      onTap: () => context.push('/premium'),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: AppColors.surfaceVariant,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: AppColors.accent.withAlpha(80)),
        ),
        child: Row(
          children: [
            const Icon(Icons.auto_awesome, color: AppColors.accent),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Upgrade to Premium', style: AppTypography.headingSmall),
                  const SizedBox(height: 2),
                  Text('Unlimited analyses & more', style: AppTypography.bodySmall),
                ],
              ),
            ),
            const Icon(Icons.chevron_right, color: AppColors.textTertiary),
          ],
        ),
      ),
    );
  }

  Widget _buildOfflineAiSection() {
    final gemma = ref.watch(gemmaProvider);

    // Show confirmation dialog when download is blocked
    ref.listen<GemmaState>(gemmaProvider, (prev, next) {
      if (prev?.downloadBlock == next.downloadBlock) return;
      if (next.downloadBlock == DownloadBlock.cellular) {
        _showDownloadWarning(
          title: 'No Wi-Fi Detected',
          message: 'This will download ~3.4 GB using mobile data. Continue?',
        );
      } else if (next.downloadBlock == DownloadBlock.lowStorage) {
        _showDownloadWarning(
          title: 'Low Storage',
          message: 'At least 4 GB of free space is recommended. Continue anyway?',
        );
      }
    });

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.surfaceVariant,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.smart_toy_outlined, size: 20, color: AppColors.accent),
              const SizedBox(width: 8),
              Text('Offline AI', style: AppTypography.headingSmall),
            ],
          ),
          const SizedBox(height: 4),
          Text(
            'On-device style tips without internet (~3.4 GB)',
            style: AppTypography.bodySmall.copyWith(color: AppColors.textSecondary),
          ),
          const SizedBox(height: 12),
          if (gemma.error != null) ...[
            Text(
              gemma.error!,
              style: AppTypography.bodySmall.copyWith(color: AppColors.error),
            ),
            const SizedBox(height: 8),
          ],
          _buildGemmaControls(gemma),
        ],
      ),
    );
  }

  Widget _buildGemmaControls(GemmaState gemma) {
    switch (gemma.downloadStatus) {
      case GemmaDownloadStatus.notDownloaded:
        return SizedBox(
          width: double.infinity,
          child: OutlinedButton.icon(
            onPressed: () => ref.read(gemmaProvider.notifier).downloadAndEnable(),
            icon: const Icon(Icons.download, size: 18),
            label: const Text('Download Model'),
          ),
        );

      case GemmaDownloadStatus.downloading:
        final pct = (gemma.downloadProgress * 100).toInt();
        return Column(
          children: [
            ClipRRect(
              borderRadius: BorderRadius.circular(6),
              child: LinearProgressIndicator(
                value: gemma.downloadProgress,
                minHeight: 8,
                backgroundColor: AppColors.surface,
                valueColor: const AlwaysStoppedAnimation<Color>(AppColors.accent),
              ),
            ),
            const SizedBox(height: 6),
            Text(
              'Downloading... $pct%',
              style: AppTypography.bodySmall.copyWith(color: AppColors.textSecondary),
            ),
          ],
        );

      case GemmaDownloadStatus.installed:
        return Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Row(
              children: [
                Icon(
                  gemma.isEnabled ? Icons.check_circle : Icons.circle_outlined,
                  size: 18,
                  color: gemma.isEnabled ? AppColors.accent : AppColors.textTertiary,
                ),
                const SizedBox(width: 8),
                Text(
                  gemma.isEnabled ? 'Enabled' : 'Disabled',
                  style: AppTypography.bodyMedium,
                ),
              ],
            ),
            Row(
              children: [
                Switch(
                  value: gemma.isEnabled,
                  activeTrackColor: AppColors.accent,
                  onChanged: (on) {
                    if (on) {
                      ref.read(gemmaProvider.notifier).loadModel();
                    } else {
                      ref.read(gemmaProvider.notifier).disable();
                    }
                  },
                ),
                IconButton(
                  icon: const Icon(Icons.delete_outline, size: 20),
                  color: AppColors.textTertiary,
                  onPressed: () => _confirmDeleteModel(),
                  tooltip: 'Delete model',
                ),
              ],
            ),
          ],
        );
    }
  }

  void _showDownloadWarning({required String title, required String message}) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(title),
        content: Text(message),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
          TextButton(
            onPressed: () {
              Navigator.pop(ctx);
              ref.read(gemmaProvider.notifier).downloadAndEnable(force: true);
            },
            child: const Text('Download Anyway'),
          ),
        ],
      ),
    );
  }

  void _confirmDeleteModel() {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Delete AI Model?'),
        content: const Text('This will remove the downloaded model (~3.4 GB). You can re-download it later.'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
          TextButton(
            onPressed: () {
              Navigator.pop(ctx);
              ref.read(gemmaProvider.notifier).deleteModel();
            },
            child: Text('Delete', style: TextStyle(color: AppColors.error)),
          ),
        ],
      ),
    );
  }

  void _editNickname() {
    final controller = TextEditingController(text: _profile?['nickname'] as String? ?? '');
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Edit Nickname'),
        content: TextField(
          controller: controller,
          decoration: const InputDecoration(hintText: 'Enter nickname'),
          autofocus: true,
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
          TextButton(
            onPressed: () async {
              final nav = Navigator.of(ctx);
              final name = controller.text.trim();
              if (name.isNotEmpty) {
                await ref.read(profileServiceProvider).updateProfile(nickname: name);
                await _loadProfile();
              }
              if (mounted) nav.pop();
            },
            child: const Text('Save'),
          ),
        ],
      ),
    );
  }

  void _editStylePreference() {
    final styles = ['casual', 'minimal', 'formal', 'sporty'];
    showDialog(
      context: context,
      builder: (ctx) => SimpleDialog(
        title: const Text('Style Preference'),
        children: styles.map((s) => SimpleDialogOption(
          onPressed: () async {
            final nav = Navigator.of(ctx);
            await ref.read(profileServiceProvider).updateProfile(stylePreference: s);
            await _loadProfile();
            if (mounted) nav.pop();
          },
          child: Text(s, style: AppTypography.bodyMedium),
        )).toList(),
      ),
    );
  }
}

class _StatItem extends StatelessWidget {
  final String label;
  final String value;
  const _StatItem({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(value, style: AppTypography.headingSmall),
        const SizedBox(height: 4),
        Text(label, style: AppTypography.labelSmall.copyWith(color: AppColors.textSecondary)),
      ],
    );
  }
}

class _SettingsTile extends StatelessWidget {
  final IconData icon;
  final String title;
  final String? subtitle;
  final VoidCallback onTap;
  const _SettingsTile({required this.icon, required this.title, this.subtitle, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: Icon(icon, color: AppColors.textSecondary),
      title: Text(title, style: AppTypography.bodyMedium),
      subtitle: subtitle != null ? Text(subtitle!, style: AppTypography.bodySmall.copyWith(color: AppColors.textSecondary)) : null,
      trailing: const Icon(Icons.chevron_right, color: AppColors.textTertiary),
      onTap: onTap,
      contentPadding: EdgeInsets.zero,
    );
  }
}
