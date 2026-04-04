import '../models/clothing_item.dart';
import '../models/outfit_recommendation.dart';

class RecommendationService {
  // ── Category compatibility (pairwise, 0.0–1.0) ──

  static const Map<String, Map<String, double>> _topBottomCompat = {
    'T-shirt': {'Pants': 0.70, 'Jeans': 0.95, 'Shorts': 0.90, 'Skirt': 0.75, 'Dress': 0.0},
    'Shirt':   {'Pants': 0.95, 'Jeans': 0.85, 'Shorts': 0.65, 'Skirt': 0.90, 'Dress': 0.0},
    'Hoodie':  {'Pants': 0.70, 'Jeans': 0.95, 'Shorts': 0.80, 'Skirt': 0.55, 'Dress': 0.0},
    'Sweater': {'Pants': 0.90, 'Jeans': 0.90, 'Shorts': 0.45, 'Skirt': 0.85, 'Dress': 0.0},
    'Jacket':  {'Pants': 0.85, 'Jeans': 0.90, 'Shorts': 0.60, 'Skirt': 0.80, 'Dress': 0.90},
    'Coat':    {'Pants': 0.90, 'Jeans': 0.85, 'Shorts': 0.35, 'Skirt': 0.85, 'Dress': 0.95},
  };

  static const Map<String, Map<String, double>> _bottomShoesCompat = {
    'Pants':  {'Sneakers': 0.80, 'Boots': 0.85, 'Flats': 0.80, 'Heels': 0.85},
    'Jeans':  {'Sneakers': 0.95, 'Boots': 0.80, 'Flats': 0.75, 'Heels': 0.65},
    'Shorts': {'Sneakers': 0.95, 'Boots': 0.40, 'Flats': 0.85, 'Heels': 0.55},
    'Skirt':  {'Sneakers': 0.70, 'Boots': 0.85, 'Flats': 0.90, 'Heels': 0.95},
    'Dress':  {'Sneakers': 0.60, 'Boots': 0.85, 'Flats': 0.85, 'Heels': 0.95},
  };

  static const Map<String, Map<String, double>> _topShoesCompat = {
    'T-shirt': {'Sneakers': 0.95, 'Boots': 0.50, 'Flats': 0.75, 'Heels': 0.40},
    'Shirt':   {'Sneakers': 0.70, 'Boots': 0.85, 'Flats': 0.90, 'Heels': 0.90},
    'Hoodie':  {'Sneakers': 0.95, 'Boots': 0.60, 'Flats': 0.65, 'Heels': 0.30},
    'Sweater': {'Sneakers': 0.80, 'Boots': 0.90, 'Flats': 0.85, 'Heels': 0.75},
    'Jacket':  {'Sneakers': 0.80, 'Boots': 0.90, 'Flats': 0.80, 'Heels': 0.85},
    'Coat':    {'Sneakers': 0.65, 'Boots': 0.95, 'Flats': 0.75, 'Heels': 0.90},
  };

  static const _neutralColors = {'black', 'white', 'gray'};

  static const Map<String, Set<String>> _complementaryPairs = {
    'blue': {'beige', 'white'},
    'red': {'green', 'black', 'white'},
    'green': {'red', 'beige'},
    'beige': {'blue', 'green', 'black'},
  };

  /// Generate top 3 outfit recommendations for a given user item.
  /// [preferredStyle] adds a bonus when recommended items match the user's preference.
  List<OutfitRecommendation> recommend(ClothingItem userItem,
      {int maxResults = 3, String? preferredStyle}) {
    final slot = userItem.slot;
    List<_Candidate> candidates = [];

    if (slot == 'top' || slot == 'outer') {
      // Need bottom + shoes
      for (final bottom in ClothingItem.bottomCategories) {
        // Skip Dress when user has a top
        if (bottom == 'Dress' && slot == 'top') continue;
        for (final shoes in ClothingItem.shoesCategories) {
          for (final bColor in ClothingItem.allColors) {
            for (final sColor in ClothingItem.allColors) {
              final bottomItem = ClothingItem(
                category: bottom,
                color: bColor,
                style: _styleFor(bottom),
              );
              final shoesItem = ClothingItem(
                category: shoes,
                color: sColor,
                style: _styleFor(shoes),
              );
              final score = _scoreOutfit(userItem, [bottomItem, shoesItem], preferredStyle: preferredStyle);
              candidates.add(_Candidate([bottomItem, shoesItem], score));
            }
          }
        }
      }
    } else if (slot == 'bottom') {
      if (userItem.isDress) {
        // Dress: only need shoes (optionally jacket)
        for (final shoes in ClothingItem.shoesCategories) {
          for (final sColor in ClothingItem.allColors) {
            final shoesItem = ClothingItem(
              category: shoes,
              color: sColor,
              style: _styleFor(shoes),
            );
            final score = _scoreOutfit(userItem, [shoesItem], preferredStyle: preferredStyle);
            candidates.add(_Candidate([shoesItem], score));
          }
        }
        // Also try outer + any shoes
        for (final outer in ClothingItem.outerCategories) {
          for (final shoes in ClothingItem.shoesCategories) {
            for (final sColor in ClothingItem.allColors) {
              for (final oColor in ClothingItem.allColors) {
                final outerItem = ClothingItem(
                  category: outer,
                  color: oColor,
                  style: _styleFor(outer),
                );
                final shoesItem = ClothingItem(
                  category: shoes,
                  color: sColor,
                  style: _styleFor(shoes),
                );
                final score = _scoreOutfit(userItem, [outerItem, shoesItem], preferredStyle: preferredStyle);
                candidates.add(_Candidate([outerItem, shoesItem], score));
              }
            }
          }
        }
      } else {
        // Bottom (Pants/Jeans): need top + shoes
        for (final top in ClothingItem.topCategories) {
          for (final shoes in ClothingItem.shoesCategories) {
            for (final tColor in ClothingItem.allColors) {
              for (final sColor in ClothingItem.allColors) {
                final topItem = ClothingItem(
                  category: top,
                  color: tColor,
                  style: _styleFor(top),
                );
                final shoesItem = ClothingItem(
                  category: shoes,
                  color: sColor,
                  style: _styleFor(shoes),
                );
                final score = _scoreOutfit(userItem, [topItem, shoesItem], preferredStyle: preferredStyle);
                candidates.add(_Candidate([topItem, shoesItem], score));
              }
            }
          }
        }
      }
    } else if (slot == 'shoes') {
      // Need top + bottom
      for (final top in ClothingItem.topCategories) {
        for (final bottom in ClothingItem.bottomCategories) {
          if (bottom == 'Dress') continue;
          for (final tColor in ClothingItem.allColors) {
            for (final bColor in ClothingItem.allColors) {
              final topItem = ClothingItem(
                category: top,
                color: tColor,
                style: _styleFor(top),
              );
              final bottomItem = ClothingItem(
                category: bottom,
                color: bColor,
                style: _styleFor(bottom),
              );
              final score = _scoreOutfit(userItem, [topItem, bottomItem], preferredStyle: preferredStyle);
              candidates.add(_Candidate([topItem, bottomItem], score));
            }
          }
        }
      }
    }

    // Group by category combination to ensure variety
    final categoryGroups = <String, List<_Candidate>>{};
    for (final c in candidates) {
      final categoryKey = c.items.map((i) => i.category).join('|');
      categoryGroups.putIfAbsent(categoryKey, () => []).add(c);
    }

    // From each category group, pick:
    //   1) best overall
    //   2) best with at least one chromatic (non-neutral) color
    final picks = <_Candidate>[];
    final chromaticPicks = <_Candidate>[];

    for (final group in categoryGroups.values) {
      group.sort((a, b) => b.scores.total.compareTo(a.scores.total));
      picks.add(group.first);

      // Find best candidate with at least one chromatic color
      for (final c in group) {
        if (c.items.any((item) => !_neutralColors.contains(item.color))) {
          chromaticPicks.add(c);
          break;
        }
      }
    }

    picks.sort((a, b) => b.scores.total.compareTo(a.scores.total));
    chromaticPicks.sort((a, b) => b.scores.total.compareTo(a.scores.total));

    // Build final list with variety:
    //   #1: best overall score
    //   #2: best with chromatic color (blue, red, beige, green — not just neutrals)
    //   #3: best from a different shoe type than #1
    final selected = <_Candidate>[];
    final seenKeys = <String>{};

    // Add #1: best overall
    if (picks.isNotEmpty) {
      selected.add(picks.first);
      seenKeys.add(picks.first.items.map((i) => '${i.category}-${i.color}').join('|'));
    }

    // Add #2: best chromatic (has at least one non-neutral color)
    for (final c in chromaticPicks) {
      final key = c.items.map((i) => '${i.category}-${i.color}').join('|');
      if (!seenKeys.contains(key)) {
        selected.add(c);
        seenKeys.add(key);
        break;
      }
    }

    // Add #3: prefer a different shoe type than what's already selected
    final usedShoes = selected
        .expand((c) => c.items)
        .where((i) => ClothingItem.shoesCategories.contains(i.category))
        .map((i) => i.category)
        .toSet();

    // Try to find a candidate with a different shoe type
    for (final c in [...picks, ...chromaticPicks]) {
      if (selected.length >= maxResults) break;
      final key = c.items.map((i) => '${i.category}-${i.color}').join('|');
      if (seenKeys.contains(key)) continue;
      final shoeTypes = c.items
          .where((i) => ClothingItem.shoesCategories.contains(i.category))
          .map((i) => i.category)
          .toSet();
      if (shoeTypes.isNotEmpty && !shoeTypes.every((s) => usedShoes.contains(s))) {
        selected.add(c);
        seenKeys.add(key);
        break;
      }
    }

    // Fallback: fill remaining slots with next best
    for (final c in [...picks, ...chromaticPicks]) {
      if (selected.length >= maxResults) break;
      final key = c.items.map((i) => '${i.category}-${i.color}').join('|');
      if (!seenKeys.contains(key)) {
        selected.add(c);
        seenKeys.add(key);
      }
    }

    final results = <OutfitRecommendation>[];
    for (final c in selected) {

      results.add(OutfitRecommendation(
        userItem: userItem,
        recommendedItems: c.items,
        matchScore: c.scores.total,
        categoryScore: c.scores.category,
        colorScore: c.scores.color,
        styleScore: c.scores.style,
        matchReason: _generateReason(userItem, c.items, c.scores),
        colorHarmony: _describeColorHarmony(userItem, c.items),
        styleConsistency: _describeStyleConsistency(
            [userItem, ...c.items].map((i) => i.style).toList()),
      ));

      if (results.length >= maxResults) break;
    }

    return results;
  }

  // ── Scoring ──

  _Scores _scoreOutfit(ClothingItem user, List<ClothingItem> items, {String? preferredStyle}) {
    final all = [user, ...items];
    final catScore = _categoryCompatibility(all);
    final colScore = _colorHarmony(all);
    final styScore = _styleConsistency(all.map((i) => i.style).toList());
    var total = catScore * 0.4 + colScore * 0.35 + styScore * 0.25;

    // Style preference bonus: +5% if recommended items align with user's preferred style
    if (preferredStyle != null) {
      final matchCount = items.where((i) => i.style == preferredStyle).length;
      if (matchCount > 0) {
        total += 0.05 * (matchCount / items.length);
      }
    }

    return _Scores(catScore, colScore, styScore, total.clamp(0.0, 1.0));
  }

  double _categoryCompatibility(List<ClothingItem> items) {
    double totalScore = 0;
    int pairs = 0;

    for (int i = 0; i < items.length; i++) {
      for (int j = i + 1; j < items.length; j++) {
        final score = _pairCategoryScore(items[i].category, items[j].category);
        if (score >= 0) {
          totalScore += score;
          pairs++;
        }
      }
    }
    return pairs > 0 ? totalScore / pairs : 0.5;
  }

  double _pairCategoryScore(String a, String b) {
    // Try top-bottom
    if (_topBottomCompat.containsKey(a) &&
        _topBottomCompat[a]!.containsKey(b)) {
      return _topBottomCompat[a]![b]!;
    }
    if (_topBottomCompat.containsKey(b) &&
        _topBottomCompat[b]!.containsKey(a)) {
      return _topBottomCompat[b]![a]!;
    }
    // Try bottom-shoes
    if (_bottomShoesCompat.containsKey(a) &&
        _bottomShoesCompat[a]!.containsKey(b)) {
      return _bottomShoesCompat[a]![b]!;
    }
    if (_bottomShoesCompat.containsKey(b) &&
        _bottomShoesCompat[b]!.containsKey(a)) {
      return _bottomShoesCompat[b]![a]!;
    }
    // Try top-shoes
    if (_topShoesCompat.containsKey(a) &&
        _topShoesCompat[a]!.containsKey(b)) {
      return _topShoesCompat[a]![b]!;
    }
    if (_topShoesCompat.containsKey(b) &&
        _topShoesCompat[b]!.containsKey(a)) {
      return _topShoesCompat[b]![a]!;
    }
    return 0.5; // default for unlisted pairs
  }

  double _colorHarmony(List<ClothingItem> items) {
    double total = 0;
    int pairs = 0;
    for (int i = 0; i < items.length; i++) {
      for (int j = i + 1; j < items.length; j++) {
        total += _pairColorScore(items[i].color, items[j].color);
        pairs++;
      }
    }
    return pairs > 0 ? total / pairs : 0.5;
  }

  double _pairColorScore(String a, String b) {
    final aIsNeutral = _neutralColors.contains(a);
    final bIsNeutral = _neutralColors.contains(b);

    // Both neutral — classic and safe
    if (aIsNeutral && bIsNeutral) return 0.90;
    // One neutral + one chromatic — versatile
    if (aIsNeutral || bIsNeutral) return 0.85;
    // Same chromatic — monochrome look
    if (a == b) return 0.70;
    // Complementary pair
    if (_complementaryPairs[a]?.contains(b) == true ||
        _complementaryPairs[b]?.contains(a) == true) {
      return 0.80;
    }
    // Other chromatic combos
    return 0.45;
  }

  double _styleConsistency(List<String> styles) {
    final unique = styles.toSet();
    if (unique.length == 1) return 1.0;
    if (unique.length == 2) {
      if (unique.contains('sporty') && unique.contains('formal')) return 0.35;
      return 0.70;
    }
    return 0.40;
  }

  // ── Descriptions ──

  String _generateReason(
      ClothingItem user, List<ClothingItem> items, _Scores scores) {
    final all = [user, ...items];
    final styles = all.map((i) => i.style).toSet();

    String styleDesc;
    if (styles.length == 1) {
      styleDesc = _styleLabel(styles.first);
    } else {
      styleDesc = 'smart-casual blend';
    }

    final catNames = items.map((i) => '${i.color} ${i.category}').join(' + ');
    return '$styleDesc — pair with $catNames for a balanced look';
  }

  String _styleLabel(String style) {
    switch (style) {
      case 'casual':
        return 'Relaxed everyday style';
      case 'formal':
        return 'Polished and refined';
      case 'sporty':
        return 'Active and energetic';
      default:
        return 'Versatile mix';
    }
  }

  String _describeColorHarmony(ClothingItem user, List<ClothingItem> items) {
    final colors = [user.color, ...items.map((i) => i.color)];
    final neutralCount = colors.where((c) => _neutralColors.contains(c)).length;
    final unique = colors.toSet();

    if (unique.length == 1) return 'Monochrome — clean and cohesive';
    if (neutralCount == colors.length) return 'Neutral palette — timeless';
    if (neutralCount >= colors.length - 1) {
      return 'Neutral base with a color accent';
    }
    return 'Colorful contrast — eye-catching combination';
  }

  String _describeStyleConsistency(List<String> styles) {
    final unique = styles.toSet();
    if (unique.length == 1) {
      switch (unique.first) {
        case 'casual':
          return 'Fully casual — comfortable and approachable';
        case 'formal':
          return 'Fully formal — polished and professional';
        case 'sporty':
          return 'Sporty throughout — active and dynamic';
      }
    }
    if (unique.contains('casual') && unique.contains('formal')) {
      return 'Smart casual — relaxed yet put-together';
    }
    return 'Mixed styles — creative and expressive';
  }

  String _styleFor(String category) {
    const map = {
      'T-shirt': 'casual',
      'Shirt': 'formal',
      'Hoodie': 'casual',
      'Sweater': 'casual',
      'Jacket': 'formal',
      'Coat': 'formal',
      'Pants': 'formal',
      'Jeans': 'casual',
      'Shorts': 'casual',
      'Skirt': 'formal',
      'Dress': 'formal',
      'Sneakers': 'sporty',
      'Boots': 'formal',
      'Flats': 'casual',
      'Heels': 'formal',
    };
    return map[category] ?? 'casual';
  }
}

class _Candidate {
  final List<ClothingItem> items;
  final _Scores scores;
  _Candidate(this.items, this.scores);
}

class _Scores {
  final double category;
  final double color;
  final double style;
  final double total;
  const _Scores(this.category, this.color, this.style, this.total);
}
