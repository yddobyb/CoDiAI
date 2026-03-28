import 'dart:ui';

class ClothingItem {
  final String category;
  final String color;
  final String style;
  final double confidence;
  final String? imagePath;

  const ClothingItem({
    required this.category,
    required this.color,
    required this.style,
    this.confidence = 0.0,
    this.imagePath,
  });

  String get slot {
    const slotMap = {
      'T-shirt': 'top',
      'Shirt': 'top',
      'Hoodie': 'top',
      'Jacket': 'outer',
      'Pants': 'bottom',
      'Jeans': 'bottom',
      'Dress': 'bottom',
      'Sneakers': 'shoes',
      'Boots': 'shoes',
    };
    return slotMap[category] ?? 'top';
  }

  bool get isDress => category == 'Dress';

  String get icon {
    const iconMap = {
      'T-shirt': '👕',
      'Shirt': '👔',
      'Hoodie': '🧥',
      'Jacket': '🧥',
      'Pants': '👖',
      'Jeans': '👖',
      'Dress': '👗',
      'Sneakers': '👟',
      'Boots': '🥾',
    };
    return iconMap[category] ?? '👕';
  }

  Color get colorValue {
    const colorMap = {
      'black': Color(0xFF1A1A1A),
      'white': Color(0xFFF5F5F5),
      'gray': Color(0xFF808080),
      'blue': Color(0xFF2962FF),
      'red': Color(0xFFD32F2F),
      'beige': Color(0xFFD2B48C),
      'green': Color(0xFF2E7D32),
    };
    return colorMap[color] ?? const Color(0xFF808080);
  }

  static const List<String> allCategories = [
    'Boots', 'Dress', 'Hoodie', 'Jacket', 'Jeans',
    'Pants', 'Shirt', 'Sneakers', 'T-shirt',
  ];

  static const List<String> allColors = [
    'black', 'white', 'gray', 'blue', 'red', 'beige', 'green',
  ];

  static const List<String> topCategories = ['T-shirt', 'Shirt', 'Hoodie'];
  static const List<String> outerCategories = ['Jacket'];
  static const List<String> bottomCategories = ['Pants', 'Jeans', 'Dress'];
  static const List<String> shoesCategories = ['Sneakers', 'Boots'];
}
