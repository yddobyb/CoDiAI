import 'package:flutter_test/flutter_test.dart';
import 'package:fashion_codi/services/product_service.dart';

void main() {
  group('ProductService.sanitizeOrFilterValue (PostgREST .or() injection)', () {
    test('leaves normal search terms unchanged', () {
      expect(ProductService.sanitizeOrFilterValue('black hoodie'), 'black hoodie');
      expect(ProductService.sanitizeOrFilterValue('Aritzia'), 'Aritzia');
    });

    test('strips the comma so a value cannot start a new filter condition', () {
      final out =
          ProductService.sanitizeOrFilterValue('shirt,id.eq.00000000-0000-0000-0000-000000000000');
      expect(out.contains(','), isFalse);
      expect(out, 'shirt id.eq.00000000-0000-0000-0000-000000000000');
    });

    test('strips grouping parentheses', () {
      final out = ProductService.sanitizeOrFilterValue('or(name.eq.x)');
      expect(out.contains('('), isFalse);
      expect(out.contains(')'), isFalse);
      expect(out, 'or name.eq.x');
    });

    test('strips quotes and backslash, collapses whitespace', () {
      expect(ProductService.sanitizeOrFilterValue(r'a"b\c'), 'a b c');
      expect(ProductService.sanitizeOrFilterValue('a   b'), 'a b');
    });

    test('a full injection payload is neutralised (no structural chars remain)', () {
      const payload = 'x%,brand.ilike.%y%),or(price.gte.0';
      final out = ProductService.sanitizeOrFilterValue(payload);
      expect(out.contains(','), isFalse);
      expect(out.contains('('), isFalse);
      expect(out.contains(')'), isFalse);
    });
  });
}
