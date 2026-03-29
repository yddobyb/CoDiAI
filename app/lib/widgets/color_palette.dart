import 'package:flutter/material.dart';
import '../core/theme/app_colors.dart';
import '../models/clothing_item.dart';

class ColorPalette extends StatelessWidget {
  final List<ClothingItem> items;
  const ColorPalette({super.key, required this.items});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        for (int i = 0; i < items.length; i++) ...[
          if (i > 0)
            const Padding(
              padding: EdgeInsets.symmetric(horizontal: 6),
              child: Icon(Icons.add, size: 12, color: AppColors.textTertiary),
            ),
          Tooltip(
            message: '${items[i].color} ${items[i].category}',
            child: Container(
              width: 22,
              height: 22,
              decoration: BoxDecoration(
                color: AppColors.clothingColor(items[i].color),
                shape: BoxShape.circle,
                border: Border.all(
                  color: items[i].color == 'white'
                      ? AppColors.border
                      : Colors.transparent,
                  width: 1.5,
                ),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withAlpha(15),
                    blurRadius: 4,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
            ),
          ),
        ],
      ],
    );
  }
}
