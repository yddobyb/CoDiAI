import 'package:flutter/foundation.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../models/product.dart';

class ProductService {
  final SupabaseClient _client = Supabase.instance.client;

  /// Fetch products with optional filters, sorting, and pagination.
  Future<List<Product>> fetchProducts({
    String? category,
    String? color,
    String? style,
    int? minPrice,
    int? maxPrice,
    String sortBy = 'created_at',
    bool ascending = false,
    int limit = 20,
    int offset = 0,
  }) async {
    var query = _client.from('products').select();

    if (category != null) query = query.eq('category', category);
    if (color != null) query = query.eq('color', color);
    if (style != null) query = query.eq('style', style);
    if (minPrice != null) query = query.gte('price', minPrice);
    if (maxPrice != null) query = query.lte('price', maxPrice);

    final data = await query
        .order(sortBy, ascending: ascending)
        .range(offset, offset + limit - 1);

    debugPrint('[Product] Fetched ${data.length} products '
        '(cat=$category, color=$color, sort=$sortBy)');

    return data.map((row) => Product.fromMap(row)).toList();
  }

  /// Fetch products matching a specific slot (top/bottom/outer/shoes).
  /// Useful for finding products that match a recommended clothing item.
  Future<List<Product>> fetchBySlot({
    required String slot,
    String? color,
    int limit = 10,
  }) async {
    const slotCategories = {
      'top': ['T-shirt', 'Shirt', 'Hoodie', 'Sweater'],
      'outer': ['Jacket', 'Coat'],
      'bottom': ['Pants', 'Jeans', 'Shorts', 'Skirt', 'Dress'],
      'shoes': ['Sneakers', 'Boots', 'Flats', 'Heels'],
    };

    final categories = slotCategories[slot];
    if (categories == null) return [];

    var query = _client
        .from('products')
        .select()
        .inFilter('category', categories);

    if (color != null) query = query.eq('color', color);

    final data = await query.order('created_at', ascending: false).limit(limit);
    return data.map((row) => Product.fromMap(row)).toList();
  }

  /// Fetch a single product by ID.
  Future<Product> fetchById(String id) async {
    final data = await _client
        .from('products')
        .select()
        .eq('id', id)
        .single();
    return Product.fromMap(data);
  }

  /// Search products by name or brand (case-insensitive).
  Future<List<Product>> search(String query, {int limit = 20}) async {
    final data = await _client
        .from('products')
        .select()
        .or('name.ilike.%$query%,brand.ilike.%$query%')
        .order('created_at', ascending: false)
        .limit(limit);

    debugPrint('[Product] Search "$query" → ${data.length} results');
    return data.map((row) => Product.fromMap(row)).toList();
  }

  /// Find similar products using metadata matching.
  /// Scores: category 0.40 + color 0.35 + style 0.25, sorted descending.
  Future<List<Product>> findSimilar({
    required String category,
    required String color,
    required String style,
    String? excludeId,
    int? minPrice,
    int? maxPrice,
    String? brandFilter,
    int limit = 20,
  }) async {
    // Fetch candidates: same category OR same color (broader pool)
    var query = _client
        .from('products')
        .select()
        .or('category.eq.$category,color.eq.$color');

    if (minPrice != null) query = query.gte('price', minPrice);
    if (maxPrice != null) query = query.lte('price', maxPrice);
    if (brandFilter != null) query = query.eq('brand', brandFilter);

    final data = await query.limit(100);
    var products = data.map((row) => Product.fromMap(row)).toList();

    // Exclude source product
    if (excludeId != null) {
      products = products.where((p) => p.id != excludeId).toList();
    }

    // Score and sort
    products.sort((a, b) {
      final sa = _similarityScore(a, category, color, style);
      final sb = _similarityScore(b, category, color, style);
      return sb.compareTo(sa);
    });

    debugPrint('[Product] Found ${products.length} similar to $color $category');
    return products.take(limit).toList();
  }

  double _similarityScore(Product p, String category, String color, String style) {
    double score = 0;
    if (p.category == category) score += 0.40;
    if (p.color == color) score += 0.35;
    if (p.style == style) score += 0.25;
    return score;
  }

  /// Get distinct brand names from products table.
  Future<List<String>> fetchBrands() async {
    final data = await _client
        .from('products')
        .select('brand')
        .order('brand');
    final brands = (data as List)
        .map((row) => row['brand'] as String)
        .toSet()
        .toList();
    brands.sort();
    return brands;
  }

  /// Fetch products matching a recommended clothing item (category + color).
  Future<List<Product>> fetchMatchingProducts({
    required String category,
    required String color,
    int limit = 5,
  }) async {
    // Exact match first
    var data = await _client
        .from('products')
        .select()
        .eq('category', category)
        .eq('color', color)
        .order('created_at', ascending: false)
        .limit(limit);

    // If too few, relax color constraint
    if (data.length < 3) {
      data = await _client
          .from('products')
          .select()
          .eq('category', category)
          .order('created_at', ascending: false)
          .limit(limit);
    }

    return data.map((row) => Product.fromMap(row)).toList();
  }
}
