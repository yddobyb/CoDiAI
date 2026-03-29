import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/ml_service.dart';
import '../services/recommendation_service.dart';
import '../services/llm_service.dart';

final mlServiceProvider = Provider<MlService>((ref) => MlService());
final recommendationServiceProvider = Provider<RecommendationService>((ref) => RecommendationService());
final llmServiceProvider = Provider<LlmService>((ref) => LlmService());
