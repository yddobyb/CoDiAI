import 'package:flutter/foundation.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

class AuthService {
  final SupabaseClient _client = Supabase.instance.client;

  User? get currentUser => _client.auth.currentUser;
  bool get isLoggedIn => currentUser != null;

  Stream<AuthState> get authStateChanges => _client.auth.onAuthStateChange;

  /// Returns true if email confirmation is needed, false if auto-logged in.
  Future<bool> signUp({required String email, required String password}) async {
    final res = await _client.auth.signUp(email: email, password: password);
    if (res.user == null) throw Exception('Sign up failed');

    // If session exists, user is auto-confirmed and logged in
    if (res.session != null) {
      debugPrint('[Auth] Sign up + auto login: ${res.user!.email}');
      return false;
    }

    // No session = email confirmation required
    debugPrint('[Auth] Sign up success, email confirmation needed: ${res.user!.email}');
    return true;
  }

  Future<void> signIn({required String email, required String password}) async {
    await _client.auth.signInWithPassword(email: email, password: password);
    debugPrint('[Auth] Sign in success: $email');
  }

  Future<void> signOut() async {
    await _client.auth.signOut();
    debugPrint('[Auth] Signed out');
  }

  Future<void> resetPassword(String email) async {
    await _client.auth.resetPasswordForEmail(email);
    debugPrint('[Auth] Password reset email sent to $email');
  }
}
