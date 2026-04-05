import 'dart:ui';

class ClothingItem {
  final String category;
  final String color;
  final String style;
  final String? season;
  final double confidence;
  final String? imagePath;

  const ClothingItem({
    required this.category,
    required this.color,
    required this.style,
    this.season,
    this.confidence = 0.0,
    this.imagePath,
  });

  String get slot {
    const slotMap = {
      'T-shirt': 'top',
      'Shirt': 'top',
      'Hoodie': 'top',
      'Sweater': 'top',
      'Jacket': 'outer',
      'Coat': 'outer',
      'Pants': 'bottom',
      'Jeans': 'bottom',
      'Shorts': 'bottom',
      'Skirt': 'bottom',
      'Dress': 'bottom',
      'Sneakers': 'shoes',
      'Boots': 'shoes',
      'Flats': 'shoes',
      'Heels': 'shoes',
    };
    return slotMap[category] ?? 'top';
  }

  bool get isDress => category == 'Dress';

  String get icon {
    const iconMap = {
      'T-shirt': '👕',
      'Shirt': '👔',
      'Hoodie': '🧥',
      'Sweater': '🧶',
      'Jacket': '🧥',
      'Coat': '🧥',
      'Pants': '👖',
      'Jeans': '👖',
      'Shorts': '🩳',
      'Skirt': '👗',
      'Dress': '👗',
      'Sneakers': '👟',
      'Boots': '🥾',
      'Flats': '👞',
      'Heels': '👠',
    };
    return iconMap[category] ?? '👕';
  }

  Color get colorValue {
    const colorMap = {
      'black': Color(0xFF1A1A1A),
      'white': Color(0xFFF5F5F5),
      'gray': Color(0xFF808080),
      'navy': Color(0xFF1A237E),
      'blue': Color(0xFF2962FF),
      'red': Color(0xFFD32F2F),
      'pink': Color(0xFFE91E63),
      'brown': Color(0xFF795548),
      'beige': Color(0xFFD2B48C),
      'green': Color(0xFF2E7D32),
      'yellow': Color(0xFFFDD835),
      'purple': Color(0xFF7B1FA2),
    };
    return colorMap[color] ?? const Color(0xFF808080);
  }

  static const List<String> allCategories = [
    'Boots', 'Coat', 'Dress', 'Flats', 'Heels', 'Hoodie',
    'Jacket', 'Jeans', 'Pants', 'Shirt', 'Shorts', 'Skirt',
    'Sneakers', 'Sweater', 'T-shirt',
  ];

  static const List<String> allColors = [
    'black', 'white', 'gray', 'navy', 'blue', 'red', 'pink',
    'brown', 'beige', 'green', 'yellow', 'purple',
  ];

  static const List<String> allSeasons = ['spring', 'summer', 'fall', 'winter'];

  String get seasonIcon {
    const map = {
      'spring': '🌸', 'summer': '☀️', 'fall': '🍂', 'winter': '❄️',
    };
    return map[season] ?? '';
  }

  String get seasonLabel {
    const map = {
      'spring': 'Spring', 'summer': 'Summer', 'fall': 'Fall', 'winter': 'Winter',
    };
    return map[season] ?? '';
  }

  static const List<String> topCategories = ['T-shirt', 'Shirt', 'Hoodie', 'Sweater'];
  static const List<String> outerCategories = ['Jacket', 'Coat'];
  static const List<String> bottomCategories = ['Pants', 'Jeans', 'Shorts', 'Skirt', 'Dress'];
  static const List<String> shoesCategories = ['Sneakers', 'Boots', 'Flats', 'Heels'];
}
