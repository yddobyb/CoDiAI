import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

class UsageService {
  final SupabaseClient _client = Supabase.instance.client;

  static const int freeAnalysisLimit = 3;
  static const String _localKeyPrefix = 'usage_analysis_';

  String? get _userId => _client.auth.currentUser?.id;
  bool get _isLoggedIn => _userId != null;

  String get _todayKey => _localKeyPrefix + DateTime.now().toIso8601String().substring(0, 10);

  /// Check if user can perform analysis. Returns remaining count.
  Future<int> getRemainingAnalyses({required bool isPremium}) async {
    if (isPremium) return 999;

    final used = await _getTodayCount();
    return (freeAnalysisLimit - used).clamp(0, freeAnalysisLimit);
  }

  /// Increment analysis count. Returns true if allowed, false if limit reached.
  Future<bool> recordAnalysis({required bool isPremium}) async {
    if (isPremium) return true;

    final used = await _getTodayCount();
    if (used >= freeAnalysisLimit) return false;

    await _incrementCount();
    debugPrint('[Usage] Analysis ${used + 1}/$freeAnalysisLimit today');
    return true;
  }

  Future<int> _getTodayCount() async {
    if (_isLoggedIn) {
      return _getRemoteCount();
    }
    return _getLocalCount();
  }

  Future<void> _incrementCount() async {
    if (_isLoggedIn) {
      await _incrementRemote();
    } else {
      await _incrementLocal();
    }
  }

  // ── Remote (Supabase) for logged-in users ──

  Future<int> _getRemoteCount() async {
    try {
      final today = DateTime.now().toIso8601String().substring(0, 10);
      final data = await _client
          .from('daily_usage')
          .select('analysis_count')
          .eq('user_id', _userId!)
          .eq('usage_date', today)
          .maybeSingle();
      return (data?['analysis_count'] as int?) ?? 0;
    } catch (e) {
      debugPrint('[Usage] Remote fetch failed: $e');
      return 0;
    }
  }

  Future<void> _incrementRemote() async {
    try {
      final today = DateTime.now().toIso8601String().substring(0, 10);
      await _client.from('daily_usage').upsert(
        {
          'user_id': _userId!,
          'usage_date': today,
          'analysis_count': (await _getRemoteCount()) + 1,
        },
        onConflict: 'user_id,usage_date',
      );
    } catch (e) {
      debugPrint('[Usage] Remote increment failed: $e');
    }
  }

  // ── Local (SharedPreferences) for anonymous users ──

  Future<int> _getLocalCount() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getInt(_todayKey) ?? 0;
  }

  Future<void> _incrementLocal() async {
    final prefs = await SharedPreferences.getInstance();
    final current = prefs.getInt(_todayKey) ?? 0;
    await prefs.setInt(_todayKey, current + 1);
  }
}
