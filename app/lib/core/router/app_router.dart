import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../models/clothing_item.dart';
import '../../features/home/home_screen.dart';
import '../../features/analysis/upload_screen.dart';
import '../../features/recommendation/result_screen.dart';
import '../../features/closet/closet_screen.dart';
import '../../features/history/history_screen.dart';
import '../../features/profile/profile_screen.dart';
import '../../features/auth/auth_screen.dart';
import '../../features/shop/shop_screen.dart';
import '../../features/shop/product_detail_screen.dart';
import '../../models/product.dart';
import '../../widgets/app_shell.dart';

final _rootNavigatorKey = GlobalKey<NavigatorState>();

final appRouter = GoRouter(
  navigatorKey: _rootNavigatorKey,
  initialLocation: '/',
  routes: [
    // ── Bottom Navigation Shell ──
    StatefulShellRoute.indexedStack(
      builder: (context, state, navigationShell) {
        return AppShell(navigationShell: navigationShell);
      },
      branches: [
        // Tab 0: Home
        StatefulShellBranch(routes: [
          GoRoute(
            path: '/',
            name: 'home',
            pageBuilder: (context, state) => CustomTransitionPage(
              key: state.pageKey,
              child: const HomeScreen(),
              transitionsBuilder: (_, animation, secondaryAnimation, child) =>
                  FadeTransition(opacity: animation, child: child),
            ),
          ),
        ]),

        // Tab 1: Shop
        StatefulShellBranch(routes: [
          GoRoute(
            path: '/shop',
            name: 'shop',
            pageBuilder: (context, state) => CustomTransitionPage(
              key: state.pageKey,
              child: const ShopScreen(),
              transitionsBuilder: (_, animation, secondaryAnimation, child) =>
                  FadeTransition(opacity: animation, child: child),
            ),
          ),
        ]),

        // Tab 2: Closet
        StatefulShellBranch(routes: [
          GoRoute(
            path: '/closet',
            name: 'closet',
            pageBuilder: (context, state) => CustomTransitionPage(
              key: state.pageKey,
              child: const ClosetScreen(),
              transitionsBuilder: (_, animation, secondaryAnimation, child) =>
                  FadeTransition(opacity: animation, child: child),
            ),
          ),
        ]),

        // Tab 2: History
        StatefulShellBranch(routes: [
          GoRoute(
            path: '/history',
            name: 'history',
            pageBuilder: (context, state) => CustomTransitionPage(
              key: state.pageKey,
              child: const HistoryScreen(),
              transitionsBuilder: (_, animation, secondaryAnimation, child) =>
                  FadeTransition(opacity: animation, child: child),
            ),
          ),
        ]),

        // Tab 3: Profile
        StatefulShellBranch(routes: [
          GoRoute(
            path: '/profile',
            name: 'profile',
            pageBuilder: (context, state) => CustomTransitionPage(
              key: state.pageKey,
              child: const ProfileScreen(),
              transitionsBuilder: (_, animation, secondaryAnimation, child) =>
                  FadeTransition(opacity: animation, child: child),
            ),
          ),
        ]),
      ],
    ),

    // ── Full-screen routes (no bottom nav) ──
    GoRoute(
      path: '/analysis',
      name: 'analysis',
      parentNavigatorKey: _rootNavigatorKey,
      pageBuilder: (context, state) {
        final imagePath = state.extra as String? ?? '';
        return CustomTransitionPage(
          key: state.pageKey,
          child: UploadScreen(imagePath: imagePath),
          transitionsBuilder: (_, animation, secondaryAnimation, child) {
            final tween = Tween(begin: const Offset(1.0, 0.0), end: Offset.zero)
                .chain(CurveTween(curve: Curves.easeOutCubic));
            return SlideTransition(position: animation.drive(tween), child: child);
          },
        );
      },
    ),
    GoRoute(
      path: '/result',
      name: 'result',
      parentNavigatorKey: _rootNavigatorKey,
      redirect: (context, state) {
        if (state.extra is! ClothingItem) return '/';
        return null;
      },
      pageBuilder: (context, state) {
        final item = state.extra! as ClothingItem;
        return CustomTransitionPage(
          key: state.pageKey,
          child: ResultScreen(clothingItem: item),
          transitionsBuilder: (_, animation, secondaryAnimation, child) {
            return FadeTransition(
              opacity: CurveTween(curve: Curves.easeIn).animate(animation),
              child: SlideTransition(
                position: Tween(begin: const Offset(0, 0.05), end: Offset.zero)
                    .animate(CurveTween(curve: Curves.easeOutCubic).animate(animation)),
                child: child,
              ),
            );
          },
        );
      },
    ),
    GoRoute(
      path: '/product',
      name: 'product',
      parentNavigatorKey: _rootNavigatorKey,
      redirect: (context, state) {
        if (state.extra is! Product) return '/shop';
        return null;
      },
      pageBuilder: (context, state) {
        final product = state.extra! as Product;
        return CustomTransitionPage(
          key: state.pageKey,
          child: ProductDetailScreen(product: product),
          transitionsBuilder: (_, animation, secondaryAnimation, child) {
            return FadeTransition(
              opacity: CurveTween(curve: Curves.easeIn).animate(animation),
              child: SlideTransition(
                position: Tween(begin: const Offset(0, 0.05), end: Offset.zero)
                    .animate(CurveTween(curve: Curves.easeOutCubic).animate(animation)),
                child: child,
              ),
            );
          },
        );
      },
    ),
    GoRoute(
      path: '/auth',
      name: 'auth',
      parentNavigatorKey: _rootNavigatorKey,
      pageBuilder: (context, state) => CustomTransitionPage(
        key: state.pageKey,
        child: const AuthScreen(),
        transitionsBuilder: (_, animation, secondaryAnimation, child) {
          final tween = Tween(begin: const Offset(0, 1.0), end: Offset.zero)
              .chain(CurveTween(curve: Curves.easeOutCubic));
          return SlideTransition(position: animation.drive(tween), child: child);
        },
      ),
    ),
  ],
);
