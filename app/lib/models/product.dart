class Product {
  final String id;
  final String name;
  final String brand;
  final String category;
  final String color;
  final String style;
  final double price;
  final String imageUrl;
  final String? affiliateUrl;
  final DateTime createdAt;
  final double? similarity;

  const Product({
    required this.id,
    required this.name,
    required this.brand,
    required this.category,
    required this.color,
    required this.style,
    required this.price,
    required this.imageUrl,
    this.affiliateUrl,
    required this.createdAt,
    this.similarity,
  });

  factory Product.fromMap(Map<String, dynamic> map) {
    return Product(
      id: map['id'] as String,
      name: map['name'] as String,
      brand: map['brand'] as String,
      category: map['category'] as String,
      color: map['color'] as String,
      style: map['style'] as String,
      price: (map['price'] as num).toDouble(),
      imageUrl: map['image_url'] as String,
      affiliateUrl: map['affiliate_url'] as String?,
      createdAt: DateTime.parse(map['created_at'] as String),
      similarity: (map['similarity'] as num?)?.toDouble(),
    );
  }

  String get formattedPrice {
    if (price == price.truncateToDouble()) return '\$${price.toInt()}';
    return '\$${price.toStringAsFixed(2)}';
  }

  String get slot {
    const slotMap = {
      'T-shirt': 'top', 'Shirt': 'top', 'Hoodie': 'top', 'Sweater': 'top',
      'Jacket': 'outer', 'Coat': 'outer',
      'Pants': 'bottom', 'Jeans': 'bottom', 'Shorts': 'bottom',
      'Skirt': 'bottom', 'Dress': 'bottom',
      'Sneakers': 'shoes', 'Boots': 'shoes', 'Flats': 'shoes', 'Heels': 'shoes',
    };
    return slotMap[category] ?? 'top';
  }

  String get slotLabel {
    const map = {'top': 'Tops', 'outer': 'Outer', 'bottom': 'Bottoms', 'shoes': 'Shoes'};
    return map[slot] ?? 'Other';
  }
}
