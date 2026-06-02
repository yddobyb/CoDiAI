import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../core/router/app_router.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_typography.dart';

/// First-run onboarding — an editorial "lookbook" walkthrough of the CoDi flow.
/// Four spreads: capture → on-device analysis → curated outfits → shop.
class OnboardingScreen extends StatefulWidget {
  const OnboardingScreen({super.key});

  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> {
  final _controller = PageController();
  int _index = 0;

  static const _slides = <_Slide>[
    _Slide(
      title: 'Snap your\npiece',
      accent: 'Start with a single garment',
      body: 'Photograph any item from your closet — '
          'a top, a coat, a pair of jeans — or pick one from your gallery.',
      visual: _CaptureVisual(),
    ),
    _Slide(
      title: 'Read by\non-device AI',
      accent: 'Private by design',
      body: 'Our model recognizes category, colour and season right on your '
          'phone. Your photo never leaves the device.',
      visual: _AnalyzeVisual(),
    ),
    _Slide(
      title: 'Curated\noutfits',
      accent: 'Styled around what you own',
      body: 'Get complete looks balanced for colour harmony and style — '
          'personalized to your closet and taste.',
      visual: _OutfitVisual(),
    ),
    _Slide(
      title: 'Shop the\nlook',
      accent: 'Find the pieces you love',
      body: 'Discover similar items from Aritzia, Garage, Oak + Fort and more, '
          'matched to your style.',
      visual: _ShopVisual(),
    ),
  ];

  bool get _isLast => _index == _slides.length - 1;

  Future<void> _finish() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(onboardingSeenKey, true);
    onboardingSeen = true;
    if (mounted) context.go('/');
  }

  void _next() {
    if (_isLast) {
      _finish();
    } else {
      _controller.nextPage(
        duration: const Duration(milliseconds: 460),
        curve: Curves.easeOutCubic,
      );
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: Stack(
        children: [
          // Soft atmospheric accent wash, top-right.
          Positioned(
            top: -120,
            right: -110,
            child: Container(
              width: 320,
              height: 320,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: RadialGradient(
                  colors: [
                    AppColors.accentLight.withValues(alpha: 0.55),
                    AppColors.accentLight.withValues(alpha: 0.0),
                  ],
                ),
              ),
            ),
          ),

          SafeArea(
            child: Column(
              children: [
                // ── Top bar: editorial index + Skip ──
                Padding(
                  padding: const EdgeInsets.fromLTRB(24, 12, 16, 0),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.center,
                    children: [
                      _IndexLabel(index: _index, total: _slides.length),
                      const Spacer(),
                      AnimatedOpacity(
                        opacity: _isLast ? 0 : 1,
                        duration: const Duration(milliseconds: 250),
                        child: TextButton(
                          onPressed: _isLast ? null : _finish,
                          style: TextButton.styleFrom(
                            foregroundColor: AppColors.textSecondary,
                          ),
                          child: Text('Skip', style: AppTypography.labelLarge),
                        ),
                      ),
                    ],
                  ),
                ),

                // ── Pages ──
                Expanded(
                  child: PageView.builder(
                    controller: _controller,
                    onPageChanged: (i) => setState(() => _index = i),
                    itemCount: _slides.length,
                    itemBuilder: (context, i) {
                      return AnimatedBuilder(
                        animation: _controller,
                        builder: (context, _) {
                          final page = _controller.hasClients
                              ? (_controller.page ?? _controller.initialPage.toDouble())
                              : 0.0;
                          final delta = page - i;
                          return _SlideView(slide: _slides[i], delta: delta);
                        },
                      );
                    },
                  ),
                ),

                // ── Indicator + action ──
                Padding(
                  padding: const EdgeInsets.fromLTRB(24, 8, 24, 24),
                  child: Column(
                    children: [
                      _PageIndicator(index: _index, total: _slides.length),
                      const SizedBox(height: 24),
                      SizedBox(
                        width: double.infinity,
                        height: 52,
                        child: ElevatedButton(
                          onPressed: _next,
                          child: AnimatedSwitcher(
                            duration: const Duration(milliseconds: 220),
                            child: Text(
                              _isLast ? 'Get Started' : 'Next',
                              key: ValueKey(_isLast),
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────
// Slide model + layout
// ─────────────────────────────────────────────────────────────────────────

class _Slide {
  final String title;
  final String accent;
  final String body;
  final Widget visual;
  const _Slide({
    required this.title,
    required this.accent,
    required this.body,
    required this.visual,
  });
}

class _SlideView extends StatelessWidget {
  final _Slide slide;
  final double delta; // distance from the active page (-1..1 nearby)
  const _SlideView({required this.slide, required this.delta});

  @override
  Widget build(BuildContext context) {
    final t = delta.abs().clamp(0.0, 1.0);
    final contentOpacity = (1 - t * 1.4).clamp(0.0, 1.0);

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Spacer(flex: 2),

          // Hero visual drifts faster than text for depth (parallax).
          Center(
            child: Transform.translate(
              offset: Offset(-delta * 56, 0),
              child: Opacity(
                opacity: (1 - t).clamp(0.0, 1.0),
                child: SizedBox(height: 248, child: Center(child: slide.visual)),
              ),
            ),
          ),

          const Spacer(flex: 2),

          // Text block drifts gently.
          Transform.translate(
            offset: Offset(-delta * 24, 0),
            child: Opacity(
              opacity: contentOpacity,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    slide.accent,
                    style: AppTypography.accent.copyWith(fontSize: 17),
                  ),
                  const SizedBox(height: 10),
                  Text(
                    slide.title,
                    style: AppTypography.displayLarge.copyWith(height: 1.02),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    slide.body,
                    style: AppTypography.bodyLarge.copyWith(
                      color: AppColors.textSecondary,
                      height: 1.55,
                    ),
                  ),
                ],
              ),
            ),
          ),
          const Spacer(flex: 1),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────
// Top index label  "01 / 04"
// ─────────────────────────────────────────────────────────────────────────

class _IndexLabel extends StatelessWidget {
  final int index;
  final int total;
  const _IndexLabel({required this.index, required this.total});

  String _two(int n) => n.toString().padLeft(2, '0');

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.baseline,
      textBaseline: TextBaseline.alphabetic,
      children: [
        AnimatedSwitcher(
          duration: const Duration(milliseconds: 300),
          transitionBuilder: (child, anim) => FadeTransition(
            opacity: anim,
            child: SlideTransition(
              position: Tween(begin: const Offset(0, 0.4), end: Offset.zero)
                  .animate(anim),
              child: child,
            ),
          ),
          child: Text(
            _two(index + 1),
            key: ValueKey(index),
            style: AppTypography.displaySmall.copyWith(
              color: AppColors.accentDark,
              fontSize: 24,
            ),
          ),
        ),
        Text(
          ' / ${_two(total)}',
          style: AppTypography.labelMedium.copyWith(color: AppColors.textTertiary),
        ),
      ],
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────
// Elongating-pill page indicator
// ─────────────────────────────────────────────────────────────────────────

class _PageIndicator extends StatelessWidget {
  final int index;
  final int total;
  const _PageIndicator({required this.index, required this.total});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: List.generate(total, (i) {
        final active = i == index;
        return AnimatedContainer(
          duration: const Duration(milliseconds: 320),
          curve: Curves.easeOutCubic,
          margin: const EdgeInsets.symmetric(horizontal: 4),
          width: active ? 26 : 7,
          height: 7,
          decoration: BoxDecoration(
            color: active ? AppColors.accent : AppColors.accentLight,
            borderRadius: BorderRadius.circular(4),
          ),
        );
      }),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────
// Bespoke visuals — composed from shapes, no image assets
// ─────────────────────────────────────────────────────────────────────────

const _softShadow = BoxShadow(
  color: Color(0x14000000),
  blurRadius: 28,
  offset: Offset(0, 14),
);

/// 1. Snap a photo — a tilted "photo card" with a garment + camera badge.
class _CaptureVisual extends StatelessWidget {
  const _CaptureVisual();

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 220,
      height: 240,
      child: Stack(
        alignment: Alignment.center,
        children: [
          // depth plate behind
          Transform.rotate(
            angle: 0.10,
            child: Container(
              width: 150,
              height: 196,
              decoration: BoxDecoration(
                color: AppColors.accentLight.withValues(alpha: 0.5),
                borderRadius: BorderRadius.circular(20),
              ),
            ),
          ),
          // photo card
          Transform.rotate(
            angle: -0.06,
            child: Container(
              width: 158,
              height: 204,
              decoration: BoxDecoration(
                color: AppColors.surface,
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: AppColors.border),
                boxShadow: const [_softShadow],
              ),
              child: Column(
                children: [
                  const SizedBox(height: 14),
                  Expanded(
                    child: Container(
                      margin: const EdgeInsets.symmetric(horizontal: 14),
                      decoration: BoxDecoration(
                        color: AppColors.surfaceMuted,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: const Center(
                        child: Icon(Icons.checkroom,
                            size: 64, color: AppColors.accentDark),
                      ),
                    ),
                  ),
                  const SizedBox(height: 14),
                  Container(
                    width: 60,
                    height: 5,
                    decoration: BoxDecoration(
                      color: AppColors.border,
                      borderRadius: BorderRadius.circular(3),
                    ),
                  ),
                  const SizedBox(height: 14),
                ],
              ),
            ),
          ),
          // camera badge
          Positioned(
            right: 24,
            bottom: 18,
            child: Container(
              width: 52,
              height: 52,
              decoration: BoxDecoration(
                color: AppColors.primary,
                shape: BoxShape.circle,
                border: Border.all(color: AppColors.background, width: 3),
                boxShadow: const [_softShadow],
              ),
              child: const Icon(Icons.camera_alt_rounded,
                  color: AppColors.textInverse, size: 24),
            ),
          ),
        ],
      ),
    );
  }
}

/// 2. On-device analysis — a phone with sparkles, a scan sweep, an "on device" lock chip.
class _AnalyzeVisual extends StatelessWidget {
  const _AnalyzeVisual();

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 220,
      height: 240,
      child: Center(
        child: Container(
          width: 150,
          height: 214,
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: AppColors.surface,
            borderRadius: BorderRadius.circular(24),
            border: Border.all(color: AppColors.border),
            boxShadow: const [_softShadow],
          ),
          child: Column(
            children: [
              const Icon(Icons.auto_awesome, color: AppColors.accent, size: 26),
              const SizedBox(height: 14),
              // scan sweep
              Container(
                height: 3,
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(2),
                  gradient: const LinearGradient(
                    colors: [
                      AppColors.accentLight,
                      AppColors.accent,
                      AppColors.accentLight,
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 14),
              Expanded(
                child: Container(
                  width: double.infinity,
                  decoration: BoxDecoration(
                    color: AppColors.surfaceMuted,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Center(
                    child: Icon(Icons.checkroom,
                        size: 48, color: AppColors.accentDark),
                  ),
                ),
              ),
              const SizedBox(height: 12),
              // on-device lock chip
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                decoration: BoxDecoration(
                  color: AppColors.surfaceVariant,
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.lock_outline,
                        size: 12, color: AppColors.accentDark),
                    const SizedBox(width: 5),
                    Text('On device', style: AppTypography.labelSmall),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// 3. Curated outfits — three fanned garment cards + a match chip.
class _OutfitVisual extends StatelessWidget {
  const _OutfitVisual();

  Widget _card(IconData icon, Color dot, double angle, Offset offset) {
    return Transform.translate(
      offset: offset,
      child: Transform.rotate(
        angle: angle,
        child: Container(
          width: 96,
          height: 124,
          decoration: BoxDecoration(
            color: AppColors.surface,
            borderRadius: BorderRadius.circular(18),
            border: Border.all(color: AppColors.border),
            boxShadow: const [_softShadow],
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icon, size: 40, color: AppColors.accentDark),
              const SizedBox(height: 14),
              Container(
                width: 12,
                height: 12,
                decoration: BoxDecoration(color: dot, shape: BoxShape.circle),
              ),
            ],
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 240,
      height: 240,
      child: Stack(
        alignment: Alignment.center,
        children: [
          _card(Icons.checkroom, AppColors.clothingBeige, -0.18,
              const Offset(-72, 6)),
          _card(Icons.dry_cleaning_outlined, AppColors.clothingBlue, 0.16,
              const Offset(72, 6)),
          _card(Icons.style_outlined, AppColors.primary, 0.0,
              const Offset(0, -10)),
          // match chip
          Positioned(
            top: 28,
            right: 30,
            child: Container(
              padding:
                  const EdgeInsets.symmetric(horizontal: 11, vertical: 6),
              decoration: BoxDecoration(
                color: AppColors.primary,
                borderRadius: BorderRadius.circular(20),
                boxShadow: const [_softShadow],
              ),
              child: Text(
                '94% match',
                style: AppTypography.labelSmall
                    .copyWith(color: AppColors.textInverse),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

/// 4. Shop the look — a row of product tiles with a price-tag badge.
class _ShopVisual extends StatelessWidget {
  const _ShopVisual();

  Widget _tile(IconData icon, double scale) {
    return Transform.scale(
      scale: scale,
      child: Container(
        width: 74,
        height: 94,
        margin: const EdgeInsets.symmetric(horizontal: 6),
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: AppColors.border),
          boxShadow: const [_softShadow],
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 30, color: AppColors.accentDark),
            const SizedBox(height: 12),
            Container(
              width: 30,
              height: 4,
              decoration: BoxDecoration(
                color: AppColors.accentLight,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 260,
      height: 240,
      child: Stack(
        alignment: Alignment.center,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              _tile(Icons.checkroom, 0.9),
              _tile(Icons.shopping_bag_outlined, 1.06),
              _tile(Icons.dry_cleaning_outlined, 0.9),
            ],
          ),
          // price-tag badge
          Positioned(
            top: 36,
            right: 30,
            child: Transform.rotate(
              angle: -0.18,
              child: Container(
                width: 46,
                height: 46,
                decoration: BoxDecoration(
                  color: AppColors.accent,
                  shape: BoxShape.circle,
                  border: Border.all(color: AppColors.background, width: 3),
                  boxShadow: const [_softShadow],
                ),
                child: const Icon(Icons.sell_outlined,
                    color: AppColors.textInverse, size: 20),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
