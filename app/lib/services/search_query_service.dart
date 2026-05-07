import '../models/clothing_item.dart';

/// Builds natural-language search queries from ML-predicted attributes
/// and routes them to external shopping platforms popular in Canada.
class SearchQueryService {
  /// Compose an English query string from a [ClothingItem].
  /// Example: Hoodie / beige / casual / fall
  ///   → "beige hoodie women casual fall"
  String buildQuery(ClothingItem item) {
    final parts = <String>[
      item.color,
      item.category.toLowerCase(),
      'women',
      if (item.style.isNotEmpty) item.style,
      if (item.season != null && item.season!.isNotEmpty) item.season!,
    ];
    return parts.where((p) => p.isNotEmpty).join(' ');
  }

  /// Map of provider label → search URL for the given query.
  /// Order matters — UI renders in iteration order.
  Map<String, Uri> buildShopUrls(String query) {
    final q = Uri.encodeQueryComponent(query);
    return {
      'Google Shopping': Uri.parse('https://www.google.com/search?tbm=shop&q=$q'),
      'Amazon': Uri.parse('https://www.amazon.ca/s?k=$q'),
      'Aritzia': Uri.parse('https://www.aritzia.com/us/en/search?q=$q'),
      'SSENSE': Uri.parse('https://www.ssense.com/en-ca/women?q=$q'),
    };
  }
}
