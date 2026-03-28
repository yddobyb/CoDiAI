import 'clothing_item.dart';

class OutfitRecommendation {
  final ClothingItem userItem;
  final List<ClothingItem> recommendedItems;
  final double matchScore;
  final double categoryScore;
  final double colorScore;
  final double styleScore;
  final String matchReason;
  final String colorHarmony;
  final String styleConsistency;
  String? llmDescription;

  OutfitRecommendation({
    required this.userItem,
    required this.recommendedItems,
    required this.matchScore,
    required this.categoryScore,
    required this.colorScore,
    required this.styleScore,
    required this.matchReason,
    required this.colorHarmony,
    required this.styleConsistency,
    this.llmDescription,
  });

  List<ClothingItem> get allItems => [userItem, ...recommendedItems];

  int get matchPercent => (matchScore * 100).round();
}
