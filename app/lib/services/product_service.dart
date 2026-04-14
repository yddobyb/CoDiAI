import 'dart:io';

import 'package:flutter/foundation.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../core/errors/app_exception.dart';
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
    try {
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
    } on PostgrestException catch (e) {
      throw NetworkException(e.message, cause: e, statusCode: 500);
    } on SocketException catch (_) {
      throw const NetworkException('No internet connection');
    }
  }

  /// Fetch products matching a specific slot (top/bottom/outer/shoes).
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

    try {
      var query = _client
          .from('products')
          .select()
          .inFilter('category', categories);

      if (color != null) query = query.eq('color', color);

      final data = await query.order('created_at', ascending: false).limit(limit);
      return data.map((row) => Product.fromMap(row)).toList();
    } on PostgrestException catch (e) {
      throw NetworkException(e.message, cause: e, statusCode: 500);
    } on SocketException catch (_) {
      throw const NetworkException('No internet connection');
    }
  }

  /// Fetch a single product by ID.
  Future<Product> fetchById(String id) async {
    try {
      final data = await _client
          .from('products')
          .select()
          .eq('id', id)
          .single();
      return Product.fromMap(data);
    } on PostgrestException catch (e) {
      throw NetworkException(e.message, cause: e, statusCode: 500);
    } on SocketException catch (_) {
      throw const NetworkException('No internet connection');
    }
  }

  /// Search products by name or brand (case-insensitive).
  Future<List<Product>> search(String query, {int limit = 20}) async {
    try {
      final data = await _client
          .from('products')
          .select()
          .or('name.ilike.%$query%,brand.ilike.%$query%')
          .order('created_at', ascending: false)
          .limit(limit);

      debugPrint('[Product] Search "$query" → ${data.length} results');
      return data.map((row) => Product.fromMap(row)).toList();
    } on PostgrestException catch (e) {
      throw NetworkException(e.message, cause: e, statusCode: 500);
    } on SocketException catch (_) {
      throw const NetworkException('No internet connection');
    }
  }

  /// Find similar products using image embedding similarity (pgvector).
  /// Falls back to metadata matching if the source product has no embedding.
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
    // Try embedding-based search first if we have a product ID
    if (excludeId != null) {
      try {
        final results = await _findSimilarByEmbedding(
          productId: excludeId,
          minPrice: minPrice,
          maxPrice: maxPrice,
          brandFilter: brandFilter,
          limit: limit,
        );
        if (results.isNotEmpty) {
          debugPrint('[Product] Embedding search: ${results.length} similar to $color $category');
          return results;
        }
      } catch (e) {
        debugPrint('[Product] Embedding search failed, falling back to metadata: $e');
      }
    }

    // Fallback: metadata-based matching
    return _findSimilarByMetadata(
      category: category,
      color: color,
      style: style,
      excludeId: excludeId,
      minPrice: minPrice,
      maxPrice: maxPrice,
      brandFilter: brandFilter,
      limit: limit,
    );
  }

  Future<List<Product>> _findSimilarByEmbedding({
    required String productId,
    int? minPrice,
    int? maxPrice,
    String? brandFilter,
    int limit = 20,
  }) async {
    final params = <String, dynamic>{
      'source_product_id': productId,
      'match_threshold': 0.5,
      'match_count': limit,
    };
    if (brandFilter != null) params['filter_brand'] = brandFilter;
    if (minPrice != null) params['filter_min_price'] = minPrice;
    if (maxPrice != null) params['filter_max_price'] = maxPrice;

    try {
      final data = await _client.rpc('match_products_by_id', params: params);
      return (data as List).map((row) => Product.fromMap(row)).toList();
    } on PostgrestException catch (e) {
      throw NetworkException(e.message, cause: e, statusCode: 500);
    } on SocketException catch (_) {
      throw const NetworkException('No internet connection');
    }
  }

  Future<List<Product>> _findSimilarByMetadata({
    required String category,
    required String color,
    required String style,
    String? excludeId,
    int? minPrice,
    int? maxPrice,
    String? brandFilter,
    int limit = 20,
  }) async {
    try {
      var query = _client
          .from('products')
          .select()
          .or('category.eq.$category,color.eq.$color');

      if (minPrice != null) query = query.gte('price', minPrice);
      if (maxPrice != null) query = query.lte('price', maxPrice);
      if (brandFilter != null) query = query.eq('brand', brandFilter);

      final data = await query.limit(100);
      var products = data.map((row) => Product.fromMap(row)).toList();

      if (excludeId != null) {
        products = products.where((p) => p.id != excludeId).toList();
      }

      products.sort((a, b) {
        final sa = _metadataScore(a, category, color, style);
        final sb = _metadataScore(b, category, color, style);
        return sb.compareTo(sa);
      });

      debugPrint('[Product] Metadata search: ${products.length} similar to $color $category');
      return products.take(limit).toList();
    } on PostgrestException catch (e) {
      throw NetworkException(e.message, cause: e, statusCode: 500);
    } on SocketException catch (_) {
      throw const NetworkException('No internet connection');
    }
  }

  double _metadataScore(Product p, String category, String color, String style) {
    double score = 0;
    if (p.category == category) score += 0.40;
    if (p.color == color) score += 0.35;
    if (p.style == style) score += 0.25;
    return score;
  }

  /// Get distinct brand names from products table.
  Future<List<String>> fetchBrands() async {
    try {
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
    } on PostgrestException catch (e) {
      throw NetworkException(e.message, cause: e, statusCode: 500);
    } on SocketException catch (_) {
      throw const NetworkException('No internet connection');
    }
  }

  /// Fetch products matching a recommended clothing item (category + color).
  Future<List<Product>> fetchMatchingProducts({
    required String category,
    required String color,
    int limit = 5,
  }) async {
    try {
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
    } on PostgrestException catch (e) {
      throw NetworkException(e.message, cause: e, statusCode: 500);
    } on SocketException catch (_) {
      throw const NetworkException('No internet connection');
    }
  }
}
