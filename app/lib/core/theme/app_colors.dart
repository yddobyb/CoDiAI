import 'package:flutter/material.dart';

abstract final class AppColors {
  // ── Background & Surface ──
  static const background = Color(0xFFFAF9F7);
  static const surface = Color(0xFFFFFFFF);
  static const surfaceVariant = Color(0xFFF3F0EC);
  static const surfaceMuted = Color(0xFFF7F5F2);

  // ── Brand ──
  static const primary = Color(0xFF1A1A1A);
  static const accent = Color(0xFFC9A87C);
  static const accentLight = Color(0xFFE8DDD3);
  static const accentDark = Color(0xFF8B7D6B);

  // ── Text ──
  static const textPrimary = Color(0xFF1A1A1A);
  static const textSecondary = Color(0xFF6B6B6B);
  static const textTertiary = Color(0xFFB0ADA8);
  static const textInverse = Color(0xFFFAF9F7);

  // ── Border & Divider ──
  static const border = Color(0xFFE8E5E1);
  static const borderLight = Color(0xFFF0EDEA);
  static const divider = Color(0xFFE8E5E1);

  // ── Status ──
  static const success = Color(0xFF6B8E6B);
  static const successLight = Color(0xFFE8F0E8);
  static const warning = Color(0xFFD4A574);
  static const warningLight = Color(0xFFFAF0E4);
  static const error = Color(0xFFC75050);
  static const errorLight = Color(0xFFFAE8E8);

  // ── Clothing Color Chips ──
  static const clothingBlack = Color(0xFF1A1A1A);
  static const clothingWhite = Color(0xFFF5F5F5);
  static const clothingGray = Color(0xFF808080);
  static const clothingBlue = Color(0xFF4A6FA5);
  static const clothingRed = Color(0xFFBF4545);
  static const clothingBeige = Color(0xFFD2B48C);
  static const clothingGreen = Color(0xFF5E8B5E);

  static Color clothingColor(String name) {
    return switch (name.toLowerCase()) {
      'black' => clothingBlack,
      'white' => clothingWhite,
      'gray' => clothingGray,
      'blue' => clothingBlue,
      'red' => clothingRed,
      'beige' => clothingBeige,
      'green' => clothingGreen,
      _ => clothingGray,
    };
  }
}
