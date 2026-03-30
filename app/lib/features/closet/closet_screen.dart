import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_typography.dart';
import '../../models/clothing_item.dart';
import '../../providers/service_providers.dart';
import 'closet_provider.dart';

class ClosetScreen extends ConsumerStatefulWidget {
  const ClosetScreen({super.key});

  @override
  ConsumerState<ClosetScreen> createState() => _ClosetScreenState();
}

class _ClosetScreenState extends ConsumerState<ClosetScreen> {
  String _selectedFilter = 'All';

  static const _filters = ['All', 'Tops', 'Bottoms', 'Outer', 'Shoes'];
  static const _filterCategories = {
    'All': null,
    'Tops': ['T-shirt', 'Shirt', 'Hoodie'],
    'Bottoms': ['Pants', 'Jeans', 'Dress'],
    'Outer': ['Jacket'],
    'Shoes': ['Sneakers', 'Boots'],
  };

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final authState = ref.read(authStateProvider);
      if (authState.value?.session != null) {
        ref.read(closetProvider.notifier).loadItems();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final auth = ref.watch(authStateProvider);
    final isLoggedIn = auth.value?.session != null;

    return Scaffold(
      appBar: AppBar(
        title: const Text('My Closet'),
        actions: [
          if (isLoggedIn)
            IconButton(
              icon: const Icon(Icons.add, size: 24),
              onPressed: () => _addItem(),
            ),
        ],
      ),
      body: isLoggedIn ? _buildCloset() : _buildLoginPrompt(),
    );
  }

  Widget _buildLoginPrompt() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.checkroom, size: 64, color: AppColors.textTertiary),
            const SizedBox(height: 20),
            Text('Your Closet', style: AppTypography.headingMedium),
            const SizedBox(height: 8),
            Text(
              'Sign in to save and manage your wardrobe',
              style: AppTypography.bodyMedium.copyWith(color: AppColors.textSecondary),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: () => context.push('/auth'),
              child: const Text('Sign In'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCloset() {
    final state = ref.watch(closetProvider);

    return Column(
      children: [
        // Filter tabs
        SizedBox(
          height: 44,
          child: ListView.separated(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 20),
            itemCount: _filters.length,
            separatorBuilder: (_, index) => const SizedBox(width: 8),
            itemBuilder: (context, i) {
              final isSelected = _selectedFilter == _filters[i];
              return GestureDetector(
                onTap: () => setState(() => _selectedFilter = _filters[i]),
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  decoration: BoxDecoration(
                    color: isSelected ? AppColors.primary : AppColors.surfaceVariant,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  alignment: Alignment.center,
                  child: Text(
                    _filters[i],
                    style: AppTypography.labelMedium.copyWith(
                      color: isSelected ? AppColors.textInverse : AppColors.textSecondary,
                    ),
                  ),
                ),
              );
            },
          ),
        ),
        const SizedBox(height: 16),

        // Grid
        Expanded(
          child: state.isLoading
              ? const Center(child: CircularProgressIndicator(strokeWidth: 2, color: AppColors.primary))
              : _buildGrid(state.items),
        ),
      ],
    );
  }

  Widget _buildGrid(List<Map<String, dynamic>> items) {
    final filtered = _filterItems(items);

    if (filtered.isEmpty) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.add_photo_alternate_outlined, size: 48, color: AppColors.textTertiary),
            const SizedBox(height: 12),
            Text('No items yet', style: AppTypography.bodyMedium.copyWith(color: AppColors.textSecondary)),
            const SizedBox(height: 4),
            Text('Tap + to add your first item', style: AppTypography.bodySmall.copyWith(color: AppColors.textTertiary)),
          ],
        ),
      );
    }

    return GridView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 3,
        crossAxisSpacing: 12,
        mainAxisSpacing: 12,
        childAspectRatio: 0.75,
      ),
      itemCount: filtered.length,
      itemBuilder: (context, i) => _ClosetItemCard(
        item: filtered[i],
        onTap: () => _onItemTap(filtered[i]),
        onLongPress: () => _onItemDelete(filtered[i]),
      ),
    );
  }

  List<Map<String, dynamic>> _filterItems(List<Map<String, dynamic>> items) {
    final categories = _filterCategories[_selectedFilter];
    if (categories == null) return items;
    return items.where((i) => categories.contains(i['category'])).toList();
  }

  void _addItem() {
    // Navigate to home to upload a new item
    context.go('/');
  }

  void _onItemTap(Map<String, dynamic> item) {
    final clothingItem = ClothingItem(
      category: item['category'] as String,
      color: item['color'] as String,
      style: item['style'] as String,
      confidence: (item['confidence'] as num).toDouble(),
    );
    context.pushNamed('result', extra: clothingItem);
  }

  void _onItemDelete(Map<String, dynamic> item) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Delete item?'),
        content: Text('Remove ${item['color']} ${item['category']} from your closet?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
          TextButton(
            onPressed: () {
              ref.read(closetProvider.notifier).deleteItem(item['id'] as String);
              Navigator.pop(ctx);
            },
            child: Text('Delete', style: TextStyle(color: AppColors.error)),
          ),
        ],
      ),
    );
  }
}

class _ClosetItemCard extends StatelessWidget {
  final Map<String, dynamic> item;
  final VoidCallback onTap;
  final VoidCallback onLongPress;

  const _ClosetItemCard({
    required this.item,
    required this.onTap,
    required this.onLongPress,
  });

  @override
  Widget build(BuildContext context) {
    final category = item['category'] as String;
    final color = item['color'] as String;
    final imageUrl = item['image_url'] as String;
    final chipColor = AppColors.clothingColor(color);

    return GestureDetector(
      onTap: onTap,
      onLongPress: onLongPress,
      child: Container(
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: AppColors.borderLight),
        ),
        clipBehavior: Clip.antiAlias,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Expanded(
              child: Image.network(
                imageUrl,
                fit: BoxFit.cover,
                errorBuilder: (_, error, stackTrace) => Container(
                  color: AppColors.surfaceVariant,
                  child: const Icon(Icons.broken_image, color: AppColors.textTertiary),
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(8),
              child: Row(
                children: [
                  Expanded(
                    child: Text(
                      category,
                      style: AppTypography.labelSmall,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  Container(
                    width: 10, height: 10,
                    decoration: BoxDecoration(
                      color: chipColor,
                      shape: BoxShape.circle,
                      border: Border.all(
                        color: color == 'white' ? AppColors.border : Colors.transparent,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
