import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'app_colors.dart';

abstract final class AppTypography {
  // ── Display — Cormorant Garamond (editorial serif) ──
  static TextStyle get displayLarge => GoogleFonts.cormorantGaramond(
        fontSize: 40,
        fontWeight: FontWeight.w600,
        color: AppColors.textPrimary,
        height: 1.1,
        letterSpacing: -0.5,
      );

  static TextStyle get displayMedium => GoogleFonts.cormorantGaramond(
        fontSize: 32,
        fontWeight: FontWeight.w600,
        color: AppColors.textPrimary,
        height: 1.15,
        letterSpacing: -0.3,
      );

  static TextStyle get displaySmall => GoogleFonts.cormorantGaramond(
        fontSize: 26,
        fontWeight: FontWeight.w600,
        color: AppColors.textPrimary,
        height: 1.2,
      );

  // ── Heading — DM Sans (clean geometric) ──
  static TextStyle get headingLarge => GoogleFonts.dmSans(
        fontSize: 22,
        fontWeight: FontWeight.w600,
        color: AppColors.textPrimary,
        height: 1.25,
      );

  static TextStyle get headingMedium => GoogleFonts.dmSans(
        fontSize: 18,
        fontWeight: FontWeight.w600,
        color: AppColors.textPrimary,
        height: 1.3,
      );

  static TextStyle get headingSmall => GoogleFonts.dmSans(
        fontSize: 16,
        fontWeight: FontWeight.w600,
        color: AppColors.textPrimary,
        height: 1.35,
      );

  // ── Body ──
  static TextStyle get bodyLarge => GoogleFonts.dmSans(
        fontSize: 16,
        fontWeight: FontWeight.w400,
        color: AppColors.textPrimary,
        height: 1.5,
      );

  static TextStyle get bodyMedium => GoogleFonts.dmSans(
        fontSize: 14,
        fontWeight: FontWeight.w400,
        color: AppColors.textSecondary,
        height: 1.5,
      );

  static TextStyle get bodySmall => GoogleFonts.dmSans(
        fontSize: 12,
        fontWeight: FontWeight.w400,
        color: AppColors.textTertiary,
        height: 1.4,
      );

  // ── Label ──
  static TextStyle get labelLarge => GoogleFonts.dmSans(
        fontSize: 14,
        fontWeight: FontWeight.w500,
        color: AppColors.textPrimary,
        height: 1.3,
        letterSpacing: 0.3,
      );

  static TextStyle get labelMedium => GoogleFonts.dmSans(
        fontSize: 12,
        fontWeight: FontWeight.w500,
        color: AppColors.textSecondary,
        height: 1.3,
        letterSpacing: 0.5,
      );

  static TextStyle get labelSmall => GoogleFonts.dmSans(
        fontSize: 10,
        fontWeight: FontWeight.w500,
        color: AppColors.textTertiary,
        height: 1.3,
        letterSpacing: 0.8,
      );

  // ── Accent — for special elements ──
  static TextStyle get accent => GoogleFonts.cormorantGaramond(
        fontSize: 18,
        fontWeight: FontWeight.w500,
        fontStyle: FontStyle.italic,
        color: AppColors.accentDark,
        height: 1.4,
      );

  // ── Button ──
  static TextStyle get buttonLarge => GoogleFonts.dmSans(
        fontSize: 16,
        fontWeight: FontWeight.w600,
        height: 1.0,
        letterSpacing: 0.5,
      );

  static TextStyle get buttonMedium => GoogleFonts.dmSans(
        fontSize: 14,
        fontWeight: FontWeight.w600,
        height: 1.0,
        letterSpacing: 0.3,
      );
}
