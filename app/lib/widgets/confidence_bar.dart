import 'package:flutter/material.dart';

class ConfidenceBar extends StatelessWidget {
  final double confidence;
  final double height;

  const ConfidenceBar({
    super.key,
    required this.confidence,
    this.height = 8,
  });

  Color get _barColor {
    if (confidence >= 0.8) return const Color(0xFF4CAF50);
    if (confidence >= 0.6) return const Color(0xFFFFC107);
    return const Color(0xFFFF5722);
  }

  @override
  Widget build(BuildContext context) {
    final percent = (confidence * 100).toStringAsFixed(1);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text(
              'Confidence',
              style: TextStyle(fontSize: 13, color: Colors.grey),
            ),
            Text(
              '$percent%',
              style: TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w600,
                color: _barColor,
              ),
            ),
          ],
        ),
        const SizedBox(height: 4),
        ClipRRect(
          borderRadius: BorderRadius.circular(4),
          child: LinearProgressIndicator(
            value: confidence,
            minHeight: height,
            backgroundColor: Colors.grey.shade200,
            valueColor: AlwaysStoppedAnimation<Color>(_barColor),
          ),
        ),
      ],
    );
  }
}
