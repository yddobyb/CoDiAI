import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_typography.dart';
import '../../providers/service_providers.dart';

class AuthScreen extends ConsumerStatefulWidget {
  const AuthScreen({super.key});

  @override
  ConsumerState<AuthScreen> createState() => _AuthScreenState();
}

class _AuthScreenState extends ConsumerState<AuthScreen> {
  bool _isLogin = true;
  bool _isLoading = false;
  bool _isSocialLoading = false;
  String? _error;
  String? _success;
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _formKey = GlobalKey<FormState>();

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() { _isLoading = true; _error = null; _success = null; });

    try {
      final auth = ref.read(authServiceProvider);
      if (_isLogin) {
        await auth.signIn(
          email: _emailController.text.trim(),
          password: _passwordController.text,
        );
        if (mounted) Navigator.of(context).pop();
      } else {
        final needsConfirmation = await auth.signUp(
          email: _emailController.text.trim(),
          password: _passwordController.text,
        );
        if (!mounted) return;
        if (needsConfirmation) {
          setState(() {
            _success = 'Account created! Please check your email to verify, then sign in.';
            _isLogin = true;
          });
        } else {
          Navigator.of(context).pop();
        }
      }
    } catch (e) {
      _handleError(e);
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _signInWithGoogle() async {
    setState(() { _isSocialLoading = true; _error = null; });
    try {
      await ref.read(authServiceProvider).signInWithGoogle();
      if (mounted) Navigator.of(context).pop();
    } catch (e) {
      _handleError(e);
    } finally {
      if (mounted) setState(() => _isSocialLoading = false);
    }
  }

  Future<void> _signInWithApple() async {
    setState(() { _isSocialLoading = true; _error = null; });
    try {
      await ref.read(authServiceProvider).signInWithApple();
      if (mounted) Navigator.of(context).pop();
    } catch (e) {
      _handleError(e);
    } finally {
      if (mounted) setState(() => _isSocialLoading = false);
    }
  }

  void _handleError(Object e) {
    if (!mounted) return;
    final msg = e.toString().replaceFirst('Exception: ', '');
    setState(() {
      if (msg.contains('cancelled') || msg.contains('canceled')) {
        _error = null; // User cancelled, no error
      } else if (msg.contains('over_email_send_rate_limit') || msg.contains('429')) {
        _error = 'Too many attempts. Please wait a moment and try again.';
      } else {
        _error = msg;
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_isLogin ? 'Sign In' : 'Create Account'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios, size: 20),
          onPressed: () => Navigator.of(context).pop(),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 24),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const SizedBox(height: 20),
              // Brand
              Text('CoDi', style: AppTypography.displayLarge, textAlign: TextAlign.center),
              const SizedBox(height: 8),
              Text(
                _isLogin ? 'Welcome back' : 'Start your style journey',
                style: AppTypography.bodyMedium.copyWith(color: AppColors.textSecondary),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 32),

              // ── Social Login ──
              _SocialButton(
                onPressed: _isSocialLoading ? null : _signInWithGoogle,
                icon: _googleIcon(),
                label: 'Continue with Google',
              ),
              const SizedBox(height: 10),
              if (Platform.isIOS) ...[
                _SocialButton(
                  onPressed: _isSocialLoading ? null : _signInWithApple,
                  icon: const Icon(Icons.apple, size: 22),
                  label: 'Continue with Apple',
                  dark: true,
                ),
                const SizedBox(height: 10),
              ],

              if (_isSocialLoading) ...[
                const Padding(
                  padding: EdgeInsets.symmetric(vertical: 8),
                  child: Center(
                    child: SizedBox(
                      width: 20, height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2, color: AppColors.accent),
                    ),
                  ),
                ),
              ],

              // ── Divider ──
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 20),
                child: Row(
                  children: [
                    Expanded(child: Divider(color: AppColors.border)),
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      child: Text('or', style: AppTypography.bodySmall.copyWith(color: AppColors.textTertiary)),
                    ),
                    Expanded(child: Divider(color: AppColors.border)),
                  ],
                ),
              ),

              // ── Email ──
              TextFormField(
                controller: _emailController,
                keyboardType: TextInputType.emailAddress,
                autocorrect: false,
                decoration: _inputDecoration('Email'),
                validator: (v) {
                  if (v == null || v.trim().isEmpty) return 'Enter your email';
                  if (!v.contains('@')) return 'Enter a valid email';
                  return null;
                },
              ),
              const SizedBox(height: 16),

              // Password
              TextFormField(
                controller: _passwordController,
                obscureText: true,
                decoration: _inputDecoration('Password'),
                validator: (v) {
                  if (v == null || v.isEmpty) return 'Enter your password';
                  if (!_isLogin && v.length < 6) return 'At least 6 characters';
                  return null;
                },
              ),
              const SizedBox(height: 24),

              // Success
              if (_success != null) ...[
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: AppColors.accent.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.check_circle_outline, color: AppColors.accent, size: 20),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          _success!,
                          style: AppTypography.bodySmall.copyWith(color: AppColors.accent),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
              ],

              // Error
              if (_error != null) ...[
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: AppColors.errorLight,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Text(
                    _error!,
                    style: AppTypography.bodySmall.copyWith(color: AppColors.error),
                    textAlign: TextAlign.center,
                  ),
                ),
                const SizedBox(height: 16),
              ],

              // Submit
              ElevatedButton(
                onPressed: _isLoading ? null : _submit,
                child: _isLoading
                    ? const SizedBox(
                        width: 20, height: 20,
                        child: CircularProgressIndicator(strokeWidth: 2, color: AppColors.textInverse),
                      )
                    : Text(_isLogin ? 'Sign In' : 'Create Account'),
              ),
              const SizedBox(height: 16),

              // Toggle
              TextButton(
                onPressed: () => setState(() {
                  _isLogin = !_isLogin;
                  _error = null;
                }),
                child: Text(
                  _isLogin ? "Don't have an account? Sign up" : 'Already have an account? Sign in',
                  style: AppTypography.bodyMedium.copyWith(color: AppColors.accent),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _googleIcon() {
    return SizedBox(
      width: 20,
      height: 20,
      child: CustomPaint(painter: _GoogleLogoPainter()),
    );
  }

  InputDecoration _inputDecoration(String label) {
    return InputDecoration(
      labelText: label,
      labelStyle: AppTypography.bodyMedium.copyWith(color: AppColors.textTertiary),
      filled: true,
      fillColor: AppColors.surfaceVariant,
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide.none,
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: AppColors.accent, width: 1.5),
      ),
      errorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: AppColors.error, width: 1),
      ),
      contentPadding: const EdgeInsets.symmetric(horizontal: 18, vertical: 16),
    );
  }
}

// ── Social Login Button ──

class _SocialButton extends StatelessWidget {
  final VoidCallback? onPressed;
  final Widget icon;
  final String label;
  final bool dark;

  const _SocialButton({
    required this.onPressed,
    required this.icon,
    required this.label,
    this.dark = false,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 50,
      child: OutlinedButton(
        onPressed: onPressed,
        style: OutlinedButton.styleFrom(
          backgroundColor: dark ? AppColors.primary : AppColors.surface,
          foregroundColor: dark ? AppColors.textInverse : AppColors.textPrimary,
          side: BorderSide(color: dark ? AppColors.primary : AppColors.border),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            icon,
            const SizedBox(width: 12),
            Text(label, style: AppTypography.bodyMedium.copyWith(
              color: dark ? AppColors.textInverse : AppColors.textPrimary,
            )),
          ],
        ),
      ),
    );
  }
}

// ── Google "G" Logo Painter ──

class _GoogleLogoPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final double w = size.width;
    final double h = size.height;
    final center = Offset(w / 2, h / 2);
    final radius = w / 2;

    // Blue arc (top-right)
    final bluePaint = Paint()..color = const Color(0xFF4285F4)..style = PaintingStyle.stroke..strokeWidth = w * 0.2;
    canvas.drawArc(Rect.fromCircle(center: center, radius: radius * 0.7), -0.9, 1.8, false, bluePaint);

    // Green arc (bottom-right)
    final greenPaint = Paint()..color = const Color(0xFF34A853)..style = PaintingStyle.stroke..strokeWidth = w * 0.2;
    canvas.drawArc(Rect.fromCircle(center: center, radius: radius * 0.7), 0.9, 1.2, false, greenPaint);

    // Yellow arc (bottom-left)
    final yellowPaint = Paint()..color = const Color(0xFFFBBC05)..style = PaintingStyle.stroke..strokeWidth = w * 0.2;
    canvas.drawArc(Rect.fromCircle(center: center, radius: radius * 0.7), 2.1, 1.0, false, yellowPaint);

    // Red arc (top-left)
    final redPaint = Paint()..color = const Color(0xFFEA4335)..style = PaintingStyle.stroke..strokeWidth = w * 0.2;
    canvas.drawArc(Rect.fromCircle(center: center, radius: radius * 0.7), -2.0, 1.1, false, redPaint);

    // Horizontal bar
    final barPaint = Paint()..color = const Color(0xFF4285F4)..style = PaintingStyle.fill;
    canvas.drawRect(Rect.fromLTWH(w * 0.5, h * 0.38, w * 0.45, h * 0.24), barPaint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
