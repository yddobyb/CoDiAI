import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

class ClosetService {
  final SupabaseClient _client = Supabase.instance.client;

  String get _userId => _client.auth.currentUser!.id;

  Future<List<Map<String, dynamic>>> fetchItems() async {
    final data = await _client
        .from('closet_items')
        .select()
        .eq('user_id', _userId)
        .order('created_at', ascending: false);
    return List<Map<String, dynamic>>.from(data);
  }

  Future<Map<String, dynamic>> addItem({
    required String imagePath,
    required String category,
    required String color,
    required String style,
    required double confidence,
  }) async {
    // Upload image
    final file = File(imagePath);
    final fileName = '${DateTime.now().millisecondsSinceEpoch}.jpg';
    final storagePath = '$_userId/$fileName';

    await _client.storage
        .from('closet-images')
        .upload(storagePath, file);

    final imageUrl = _client.storage
        .from('closet-images')
        .getPublicUrl(storagePath);

    debugPrint('[Closet] Image uploaded: $imageUrl');

    // Insert record
    final data = await _client.from('closet_items').insert({
      'user_id': _userId,
      'image_url': imageUrl,
      'category': category,
      'color': color,
      'style': style,
      'confidence': confidence,
    }).select().single();

    debugPrint('[Closet] Item added: ${data['id']}');
    return data;
  }

  Future<void> deleteItem(String id) async {
    // Get image URL to delete from storage
    final item = await _client
        .from('closet_items')
        .select('image_url')
        .eq('id', id)
        .single();

    final imageUrl = item['image_url'] as String;
    // Extract storage path from URL
    final uri = Uri.parse(imageUrl);
    final pathSegments = uri.pathSegments;
    final bucketIndex = pathSegments.indexOf('closet-images');
    if (bucketIndex >= 0 && bucketIndex + 1 < pathSegments.length) {
      final storagePath = pathSegments.sublist(bucketIndex + 1).join('/');
      await _client.storage.from('closet-images').remove([storagePath]);
    }

    await _client.from('closet_items').delete().eq('id', id);
    debugPrint('[Closet] Item deleted: $id');
  }
}
