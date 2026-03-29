import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../models/clothing_item.dart';
import '../../features/home/home_screen.dart';
import '../../features/analysis/upload_screen.dart';
import '../../features/recommendation/result_screen.dart';

final appRouter = GoRouter(
  initialLocation: '/',
  routes: [
    GoRoute(
      path: '/',
      name: 'home',
      pageBuilder: (context, state) => CustomTransitionPage(
        key: state.pageKey,
        child: const HomeScreen(),
        transitionsBuilder: (context, animation, secondaryAnimation, child) {
          return FadeTransition(opacity: animation, child: child);
        },
      ),
    ),
    GoRoute(
      path: '/analysis',
      name: 'analysis',
      pageBuilder: (context, state) {
        final imagePath = state.extra as String? ?? '';
        return CustomTransitionPage(
          key: state.pageKey,
          child: UploadScreen(imagePath: imagePath),
          transitionsBuilder: (context, animation, secondaryAnimation, child) {
            const begin = Offset(1.0, 0.0);
            const end = Offset.zero;
            final tween = Tween(begin: begin, end: end)
                .chain(CurveTween(curve: Curves.easeOutCubic));
            return SlideTransition(
              position: animation.drive(tween),
              child: child,
            );
          },
        );
      },
    ),
    GoRoute(
      path: '/result',
      name: 'result',
      redirect: (context, state) {
        if (state.extra is! ClothingItem) return '/';
        return null;
      },
      pageBuilder: (context, state) {
        final item = state.extra! as ClothingItem;
        return CustomTransitionPage(
          key: state.pageKey,
          child: ResultScreen(clothingItem: item),
          transitionsBuilder: (context, animation, secondaryAnimation, child) {
            return FadeTransition(
              opacity: CurveTween(curve: Curves.easeIn).animate(animation),
              child: SlideTransition(
                position: Tween(
                  begin: const Offset(0, 0.05),
                  end: Offset.zero,
                ).animate(CurveTween(curve: Curves.easeOutCubic).animate(animation)),
                child: child,
              ),
            );
          },
        );
      },
    ),
  ],
);
