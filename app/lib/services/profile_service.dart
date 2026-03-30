import 'package:supabase_flutter/supabase_flutter.dart';

class ProfileService {
  final SupabaseClient _client = Supabase.instance.client;

  String get _userId => _client.auth.currentUser!.id;

  Future<Map<String, dynamic>> fetchProfile() async {
    return await _client
        .from('profiles')
        .select()
        .eq('id', _userId)
        .single();
  }

  Future<void> updateProfile({
    String? nickname,
    String? stylePreference,
  }) async {
    final updates = <String, dynamic>{};
    if (nickname != null) updates['nickname'] = nickname;
    if (stylePreference != null) updates['style_preference'] = stylePreference;
    if (updates.isEmpty) return;

    await _client.from('profiles').update(updates).eq('id', _userId);
  }
}
