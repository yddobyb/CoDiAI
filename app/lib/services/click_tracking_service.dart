import 'package:flutter/foundation.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

class ClickTrackingService {
  final SupabaseClient _client = Supabase.instance.client;

  Future<void> trackClick({
    required String productId,
    String eventType = 'affiliate_click',
  }) async {
    try {
      final userId = _client.auth.currentUser?.id;
      await _client.from('click_events').insert({
        'user_id': userId,
        'product_id': productId,
        'event_type': eventType,
      });
      debugPrint('[Click] Tracked $eventType for product $productId');
    } catch (e) {
      debugPrint('[Click] Failed to track: $e');
    }
  }

  Future<int> getClickCount({
    required String productId,
    DateTime? since,
  }) async {
    var query = _client
        .from('click_events')
        .select()
        .eq('product_id', productId);
    if (since != null) {
      query = query.gte('created_at', since.toIso8601String());
    }
    final data = await query;
    return (data as List).length;
  }
}
