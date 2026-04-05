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
