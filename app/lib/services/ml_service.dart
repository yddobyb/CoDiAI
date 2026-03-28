import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:tflite_flutter/tflite_flutter.dart';
import 'package:image/image.dart' as img;
import '../models/clothing_item.dart';

class MlService {
  static const int _inputSize = 224;
  static const String _modelAsset = 'assets/fashion_category.tflite';
  static const String _labelAsset = 'assets/labels_category.txt';

  Interpreter? _interpreter;
  List<String> _labels = [];
  bool _isLoaded = false;

  bool get isLoaded => _isLoaded;

  static const Map<String, String> _categoryStyles = {
    'T-shirt': 'casual',
    'Shirt': 'formal',
    'Hoodie': 'casual',
    'Jacket': 'formal',
    'Pants': 'formal',
    'Jeans': 'casual',
    'Dress': 'formal',
    'Sneakers': 'sporty',
    'Boots': 'formal',
  };

  // Multiple reference points per color for better matching
  static const Map<String, List<List<int>>> _colorGroupRgb = {
    'black': [[30, 30, 30], [50, 50, 50]],
    'white': [[240, 240, 240], [220, 220, 225]],
    'gray': [[140, 140, 140], [170, 170, 170]],
    'blue': [[40, 80, 180], [100, 140, 190], [130, 160, 200]], // dark, medium, denim
    'red': [[190, 40, 40], [170, 50, 60]],
    'beige': [[210, 190, 160], [195, 175, 145]],
    'green': [[50, 130, 60], [80, 120, 70]],
  };

  Future<void> loadModel() async {
    try {
      _interpreter = await Interpreter.fromAsset(_modelAsset);
      final labelData = await rootBundle.loadString(_labelAsset);
      _labels = labelData
          .split('\n')
          .map((l) => l.trim())
          .where((l) => l.isNotEmpty)
          .toList();
      _isLoaded = true;
    } catch (e) {
      _isLoaded = false;
      rethrow;
    }
  }

  Future<ClothingItem> predict(String imagePath) async {
    if (!_isLoaded || _interpreter == null) {
      throw StateError('Model not loaded. Call loadModel() first.');
    }

    final stopwatch = Stopwatch()..start();

    final imageFile = File(imagePath);
    final bytes = await imageFile.readAsBytes();
    final originalImage = img.decodeImage(bytes);
    if (originalImage == null) {
      throw ArgumentError('Failed to decode image: $imagePath');
    }

    final resized =
        img.copyResize(originalImage, width: _inputSize, height: _inputSize);

    // Build input tensor [1, 224, 224, 3] with MobileNetV2 preprocessing
    var input = List.generate(
      1,
      (_) => List.generate(
        _inputSize,
        (y) => List.generate(
          _inputSize,
          (x) {
            final pixel = resized.getPixel(x, y);
            return [
              pixel.r.toDouble() / 127.5 - 1.0,
              pixel.g.toDouble() / 127.5 - 1.0,
              pixel.b.toDouble() / 127.5 - 1.0,
            ];
          },
        ),
      ),
    );

    var output = [List<double>.filled(_labels.length, 0)];
    _interpreter!.run(input, output);

    // Find top prediction
    final probs = output[0];
    int maxIdx = 0;
    double maxProb = probs[0];
    for (int i = 1; i < probs.length; i++) {
      if (probs[i] > maxProb) {
        maxProb = probs[i];
        maxIdx = i;
      }
    }

    final category = _labels[maxIdx];
    final color = _extractColor(originalImage);
    final style = _categoryStyles[category] ?? 'casual';

    stopwatch.stop();
    debugPrint('[ML] Inference completed in ${stopwatch.elapsedMilliseconds}ms — $category (${(maxProb * 100).toStringAsFixed(1)}%), color: $color');

    return ClothingItem(
      category: category,
      color: color,
      style: style,
      confidence: maxProb,
      imagePath: imagePath,
    );
  }

  /// Extract dominant color from center 40% of the image
  String _extractColor(img.Image image) {
    final startX = (image.width * 0.3).toInt();
    final endX = (image.width * 0.7).toInt();
    final startY = (image.height * 0.3).toInt();
    final endY = (image.height * 0.7).toInt();

    int totalR = 0, totalG = 0, totalB = 0;
    int count = 0;

    // Sample every 3rd pixel for speed
    for (int y = startY; y < endY; y += 3) {
      for (int x = startX; x < endX; x += 3) {
        final pixel = image.getPixel(x, y);
        totalR += pixel.r.toInt();
        totalG += pixel.g.toInt();
        totalB += pixel.b.toInt();
        count++;
      }
    }

    if (count == 0) return 'gray';

    final avgR = totalR ~/ count;
    final avgG = totalG ~/ count;
    final avgB = totalB ~/ count;

    return _nearestColorGroup(avgR, avgG, avgB);
  }

  String _nearestColorGroup(int r, int g, int b) {
    String nearest = 'gray';
    double minDist = double.infinity;

    for (final entry in _colorGroupRgb.entries) {
      // Check all reference points for this color, use the closest one
      for (final rgb in entry.value) {
        final dr = r - rgb[0];
        final dg = g - rgb[1];
        final db = b - rgb[2];
        final dist = (dr * dr + dg * dg + db * db).toDouble();
        if (dist < minDist) {
          minDist = dist;
          nearest = entry.key;
        }
      }
    }
    return nearest;
  }

  void dispose() {
    _interpreter?.close();
    _interpreter = null;
    _isLoaded = false;
  }
}
