import 'package:flutter/material.dart';
import '../models/clothing_item.dart';
import '../models/outfit_recommendation.dart';
import '../services/recommendation_service.dart';
import '../services/llm_service.dart';
import '../widgets/outfit_card.dart';

class ResultScreen extends StatefulWidget {
  final ClothingItem userItem;

  const ResultScreen({super.key, required this.userItem});

  @override
  State<ResultScreen> createState() => _ResultScreenState();
}

class _ResultScreenState extends State<ResultScreen> {
  final RecommendationService _recService = RecommendationService();
  final LlmService _llmService = LlmService();
  List<OutfitRecommendation> _recommendations = [];
  bool _isLoading = true;
  bool _llmLoading = false;

  @override
  void initState() {
    super.initState();
    _generateRecommendations();
  }

  void _generateRecommendations() {
    final recs = _recService.recommend(widget.userItem, maxResults: 3);
    setState(() {
      _recommendations = recs;
      _isLoading = false;
    });
    _fetchLlmDescriptions(recs);
  }

  Future<void> _fetchLlmDescriptions(List<OutfitRecommendation> recs) async {
    if (!_llmService.isAvailable) return;
    setState(() => _llmLoading = true);

    final descriptions = await _llmService.generateAll(recs);
    if (!mounted) return;

    setState(() {
      for (int i = 0; i < recs.length; i++) {
        recs[i].llmDescription = descriptions[i];
      }
      _llmLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final item = widget.userItem;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Outfit Ideas'),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : ListView(
              padding: const EdgeInsets.all(20),
              children: [
                // User's item summary
                Container(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: theme.colorScheme.surfaceContainerHighest
                        .withValues(alpha: 0.5),
                    borderRadius: BorderRadius.circular(14),
                  ),
                  child: Row(
                    children: [
                      Text(item.icon, style: const TextStyle(fontSize: 28)),
                      const SizedBox(width: 12),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'Your Item',
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.grey,
                            ),
                          ),
                          Text(
                            '${item.color} ${item.category}',
                            style: const TextStyle(
                              fontSize: 17,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ],
                      ),
                      const Spacer(),
                      Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: theme.colorScheme.tertiaryContainer,
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: Text(
                          item.style,
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w500,
                            color: theme.colorScheme.onTertiaryContainer,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 20),

                // Recommendations header
                Text(
                  'Recommended Outfits',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  '${_recommendations.length} combinations found',
                  style: TextStyle(fontSize: 13, color: Colors.grey.shade500),
                ),
                const SizedBox(height: 12),

                // Recommendation cards
                if (_recommendations.isEmpty)
                  Center(
                    child: Padding(
                      padding: const EdgeInsets.all(40),
                      child: Column(
                        children: [
                          Icon(Icons.search_off,
                              size: 48, color: Colors.grey.shade300),
                          const SizedBox(height: 12),
                          Text(
                            'No outfit combinations found',
                            style: TextStyle(
                              fontSize: 15,
                              color: Colors.grey.shade500,
                            ),
                          ),
                        ],
                      ),
                    ),
                  )
                else
                  ...List.generate(
                    _recommendations.length,
                    (i) => OutfitCard(
                      recommendation: _recommendations[i],
                      rank: i + 1,
                      llmLoading: _llmLoading,
                    ),
                  ),
                const SizedBox(height: 8),

                // Try another button
                SizedBox(
                  width: double.infinity,
                  height: 48,
                  child: OutlinedButton.icon(
                    onPressed: () =>
                        Navigator.popUntil(context, (route) => route.isFirst),
                    icon: const Icon(Icons.refresh_rounded, size: 20),
                    label: const Text('Try Another Item'),
                    style: OutlinedButton.styleFrom(
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(14),
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 24),
              ],
            ),
    );
  }
}
