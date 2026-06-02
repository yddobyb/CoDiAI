import 'package:flutter/material.dart';
import 'package:flutter_gemma/flutter_gemma.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'core/config/api_keys.dart';
import 'core/config/supabase_config.dart';
import 'core/theme/app_theme.dart';
import 'core/router/app_router.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Supabase.initialize(url: supabaseUrl, anonKey: supabaseAnonKey);
  await FlutterGemma.initialize(
    huggingFaceToken: huggingFaceToken.isNotEmpty ? huggingFaceToken : null,
  );
  // Decide whether to show first-run onboarding before the router builds.
  final prefs = await SharedPreferences.getInstance();
  onboardingSeen = prefs.getBool(onboardingSeenKey) ?? false;
  runApp(const ProviderScope(child: CoDiApp()));
}

class CoDiApp extends StatelessWidget {
  const CoDiApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'CoDi',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light,
      routerConfig: appRouter,
    );
  }
}
