import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../services/ml_service.dart';
import '../services/recommendation_service.dart';
import '../services/llm_service.dart';
import '../services/auth_service.dart';
import '../services/closet_service.dart';
import '../services/profile_service.dart';
import '../services/history_service.dart';
import '../services/personalization_service.dart';

final mlServiceProvider = Provider<MlService>((ref) => MlService());
final recommendationServiceProvider = Provider<RecommendationService>((ref) => RecommendationService());
final llmServiceProvider = Provider<LlmService>((ref) => LlmService());
final authServiceProvider = Provider<AuthService>((ref) => AuthService());
final closetServiceProvider = Provider<ClosetService>((ref) => ClosetService());
final profileServiceProvider = Provider<ProfileService>((ref) => ProfileService());
final historyServiceProvider = Provider<HistoryService>((ref) => HistoryService());
final personalizationServiceProvider = Provider<PersonalizationService>((ref) => PersonalizationService());

final authStateProvider = StreamProvider<AuthState>((ref) {
  return Supabase.instance.client.auth.onAuthStateChange;
});
