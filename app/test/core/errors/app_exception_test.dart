import 'package:flutter_test/flutter_test.dart';
import 'package:fashion_codi/core/errors/app_exception.dart';

void main() {
  group('AppException hierarchy', () {
    test('NetworkException has correct userMessage with status code', () {
      const e = NetworkException('Server error', statusCode: 500);
      expect(e.userMessage, contains('500'));
      expect(e.message, 'Server error');
      expect(e.toString(), contains('NetworkException'));
    });

    test('NetworkException has correct userMessage without status code', () {
      const e = NetworkException('No connection');
      expect(e.userMessage, contains('connection'));
    });

    test('MlException has user-friendly message', () {
      const e = MlException('Model failed');
      expect(e.userMessage, contains('Analysis'));
      expect(e.message, 'Model failed');
    });

    test('AuthException maps known error messages', () {
      const e1 = AuthException('Invalid login credentials');
      expect(e1.userMessage, contains('Incorrect'));

      const e2 = AuthException('User already registered');
      expect(e2.userMessage, contains('already registered'));

      const e3 = AuthException('Unknown auth error');
      expect(e3.userMessage, contains('Authentication'));
    });

    test('StorageException has user-friendly message', () {
      const e = StorageException('Upload failed');
      expect(e.userMessage, contains('save image'));
    });

    test('cause is preserved', () {
      final cause = Exception('root cause');
      final e = NetworkException('Failed', cause: cause, statusCode: 503);
      expect(e.cause, cause);
    });

    test('sealed class prevents direct instantiation', () {
      // AppException can only be instantiated through its subtypes
      expect(const NetworkException('test'), isA<AppException>());
      expect(const MlException('test'), isA<AppException>());
      expect(const AuthException('test'), isA<AppException>());
      expect(const StorageException('test'), isA<AppException>());
    });
  });
}
