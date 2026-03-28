import 'package:flutter_test/flutter_test.dart';
import 'package:fashion_codi/main.dart';

void main() {
  testWidgets('App launches smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const FashionCodiApp());
    expect(find.text('Fashion Codi AI'), findsOneWidget);
  });
}
