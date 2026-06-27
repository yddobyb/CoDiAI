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
    // Logged-in users are gated server-side: the `record_analysis` RPC checks
    // premium status + the daily free limit atomically and increments the
    // counter. The client can no longer write daily_usage directly, so the
    // limit can't be bypassed by tampering with the count or skipping the
    // local check. `isPremium` here is only a UI hint; the server decides.
    if (_isLoggedIn) return _recordRemote();

    // Anonymous users have no server identity; the local counter is a soft
    // limit (resettable by reinstall — unavoidable without an account).
    if (isPremium) return true;
    final used = await _getLocalCount();
    if (used >= freeAnalysisLimit) return false;
    await _incrementLocal();
    debugPrint('[Usage] Analysis ${used + 1}/$freeAnalysisLimit today (local)');
    return true;
  }

  /// Calls the server-side gate. Returns true if the analysis was allowed.
  /// Fails open on transient/network errors so a flaky connection doesn't block
  /// a legitimate user — the server stays authoritative whenever reachable.
  Future<bool> _recordRemote() async {
    try {
      final result = await _client.rpc('record_analysis');
      final remaining = (result as int?) ?? -1;
      if (remaining < 0) {
        debugPrint('[Usage] Daily free limit reached');
        return false;
      }
      debugPrint('[Usage] Analysis recorded, $remaining remaining today');
      return true;
    } catch (e) {
      debugPrint('[Usage] Remote record failed (fail-open): $e');
      return true;
    }
  }

  Future<int> _getTodayCount() async {
    if (_isLoggedIn) {
      return _getRemoteCount();
    }
    return _getLocalCount();
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
