import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_typography.dart';
import '../../providers/service_providers.dart';
import '../closet/closet_provider.dart';

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
      if (mounted) setState(() { _profile = profile; _isLoading = false; });
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
            borderRadius: BorderRadius.circular(14),
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
