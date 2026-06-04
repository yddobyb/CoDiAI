import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:url_launcher/url_launcher.dart';
import '../core/theme/app_colors.dart';
import '../core/theme/app_typography.dart';
import '../models/clothing_item.dart';
import '../providers/service_providers.dart';

/// A compact row of "Search on …" chips that opens the user's predicted
/// item as a query on external shopping platforms.
class ExternalSearchChips extends ConsumerWidget {
  final ClothingItem item;

  const ExternalSearchChips({super.key, required this.item});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final svc = ref.read(searchQueryServiceProvider);
    final query = svc.buildQuery(item);
    final urls = svc.buildShopUrls(query);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            const Icon(Icons.search, size: 14, color: AppColors.textTertiary),
            const SizedBox(width: 6),
            Expanded(
              child: Text(
                'Search "$query" on',
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: AppTypography.labelMedium.copyWith(color: AppColors.textTertiary),
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [
            for (final entry in urls.entries)
              ActionChip(
                label: Text(entry.key, style: AppTypography.labelMedium),
                avatar: const Icon(Icons.open_in_new, size: 13, color: AppColors.textSecondary),
                backgroundColor: AppColors.surfaceVariant,
                side: BorderSide.none,
                shape: const StadiumBorder(),
                onPressed: () => _open(entry.value),
              ),
          ],
        ),
      ],
    );
  }

  Future<void> _open(Uri uri) async {
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    }
  }
}
