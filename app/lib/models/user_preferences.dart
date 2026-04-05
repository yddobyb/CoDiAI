/// Aggregated user preference signals for recommendation personalization.
///
/// Built from three sources:
///   1. Profile style preference (explicit setting)
///   2. Closet color/style frequency (implicit behavior)
///   3. History feedback — liked/disliked outfit patterns
class UserPreferences {
  /// Explicit style preference from profile settings.
  final String? profileStyle;

  /// Color frequency from closet items, normalized 0–1 (1 = most owned color).
  final Map<String, double> colorAffinity;

  /// Style frequency from closet items, normalized 0–1.
  final Map<String, double> styleAffinity;

  /// Feedback-learned color pair bias (-1 to +1).
  /// Key: sorted pair "colorA|colorB", Value: positive = liked, negative = disliked.
  final Map<String, double> colorPairBias;

  /// Feedback-learned category pair bias (-1 to +1).
  /// Key: sorted pair "CategoryA|CategoryB".
  final Map<String, double> categoryPairBias;

  const UserPreferences({
    this.profileStyle,
    this.colorAffinity = const {},
    this.styleAffinity = const {},
    this.colorPairBias = const {},
    this.categoryPairBias = const {},
  });

  bool get hasClosetData => colorAffinity.isNotEmpty || styleAffinity.isNotEmpty;
  bool get hasFeedback => colorPairBias.isNotEmpty || categoryPairBias.isNotEmpty;
}
