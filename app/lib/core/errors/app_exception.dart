sealed class AppException implements Exception {
  final String message;
  final Object? cause;

  const AppException(this.message, {this.cause});

  @override
  String toString() => '$runtimeType: $message';
}

class NetworkException extends AppException {
  final int? statusCode;

  const NetworkException(super.message, {super.cause, this.statusCode});

  String get userMessage => statusCode != null
      ? 'Server error ($statusCode). Please try again.'
      : 'Network error. Check your connection.';
}

class MlException extends AppException {
  const MlException(super.message, {super.cause});

  String get userMessage => 'Analysis failed. Please try another photo.';
}

class AuthException extends AppException {
  const AuthException(super.message, {super.cause});

  String get userMessage => switch (message) {
        'Invalid login credentials' => 'Incorrect email or password.',
        'User already registered' => 'This email is already registered.',
        _ => 'Authentication error. Please try again.',
      };
}

class StorageException extends AppException {
  const StorageException(super.message, {super.cause});

  String get userMessage => 'Failed to save image. Please try again.';
}
