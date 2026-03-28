import 'package:flutter/material.dart';
import '../models/clothing_item.dart';

class ColorPalette extends StatelessWidget {
  final List<ClothingItem> items;
  final double dotSize;

  const ColorPalette({
    super.key,
    required this.items,
    this.dotSize = 24,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        for (int i = 0; i < items.length; i++) ...[
          if (i > 0)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 2),
              child: Icon(Icons.add, size: 12, color: Colors.grey.shade400),
            ),
          _ColorDot(
            color: items[i].colorValue,
            label: items[i].color,
            size: dotSize,
          ),
        ],
      ],
    );
  }
}

class _ColorDot extends StatelessWidget {
  final Color color;
  final String label;
  final double size;

  const _ColorDot({
    required this.color,
    required this.label,
    required this.size,
  });

  @override
  Widget build(BuildContext context) {
    return Tooltip(
      message: label,
      child: Container(
        width: size,
        height: size,
        decoration: BoxDecoration(
          color: color,
          shape: BoxShape.circle,
          border: Border.all(color: Colors.grey.shade300, width: 1.5),
          boxShadow: [
            BoxShadow(
              color: color.withValues(alpha: 0.3),
              blurRadius: 4,
              offset: const Offset(0, 1),
            ),
          ],
        ),
      ),
    );
  }
}
