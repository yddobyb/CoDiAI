import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'service_providers.dart';

/// Tracks whether the current user has premium status.
final premiumProvider = FutureProvider<bool>((ref) async {
  final authState = ref.watch(authStateProvider);
  final session = authState.value?.session;
  if (session == null) return false;

  try {
    final profile = await ref.read(profileServiceProvider).fetchProfile();
    return profile['is_premium'] as bool? ?? false;
  } catch (e) {
    debugPrint('[Premium] Failed to fetch status: $e');
    return false;
  }
});
