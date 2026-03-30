import 'package:flutter/foundation.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

class AuthService {
  final SupabaseClient _client = Supabase.instance.client;

  User? get currentUser => _client.auth.currentUser;
  bool get isLoggedIn => currentUser != null;

  Stream<AuthState> get authStateChanges => _client.auth.onAuthStateChange;

  Future<void> signUp({required String email, required String password}) async {
    final res = await _client.auth.signUp(email: email, password: password);
    if (res.user == null) throw Exception('Sign up failed');
    debugPrint('[Auth] Sign up success: ${res.user!.email}');
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
