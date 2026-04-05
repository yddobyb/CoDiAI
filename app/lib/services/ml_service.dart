import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:tflite_flutter/tflite_flutter.dart';
import 'package:image/image.dart' as img;
import '../models/clothing_item.dart';

class MlService {
  static const int _inputSize = 224;

  // Multi-task model (v5) assets
  static const String _multitaskModelAsset = 'assets/fashion_multitask.tflite';
  static const String _catLabelAsset = 'assets/labels_category.txt';
  static const String _colLabelAsset = 'assets/labels_color.txt';
  static const String _seaLabelAsset = 'assets/labels_season.txt';

  // Legacy single-task model (v4) fallback
  static const String _legacyModelAsset = 'assets/fashion_category.tflite';

  Interpreter? _interpreter;
  List<String> _catLabels = [];
  List<String> _colLabels = [];
  List<String> _seaLabels = [];
  bool _isLoaded = false;
  bool _isMultitask = false;

  bool get isLoaded => _isLoaded;

  static const Map<String, String> _categoryStyles = {
    'T-shirt': 'casual',
    'Shirt': 'formal',
    'Hoodie': 'casual',
    'Sweater': 'casual',
    'Jacket': 'formal',
    'Coat': 'formal',
    'Pants': 'formal',
    'Jeans': 'casual',
    'Shorts': 'casual',
    'Skirt': 'formal',
    'Dress': 'formal',
    'Sneakers': 'sporty',
    'Boots': 'formal',
    'Flats': 'casual',
    'Heels': 'formal',
  };

  // Pixel-based color fallback reference points
  static const Map<String, List<List<int>>> _colorGroupRgb = {
    'black': [[30, 30, 30], [50, 50, 50]],
    'white': [[240, 240, 240], [220, 220, 225]],
    'gray': [[140, 140, 140], [170, 170, 170]],
    'navy': [[0, 0, 80], [20, 25, 70], [30, 40, 100]],
    'blue': [[40, 80, 180], [100, 140, 200], [70, 120, 200]],
    'red': [[190, 40, 40], [170, 50, 60]],
    'pink': [[255, 130, 170], [220, 110, 140], [240, 160, 180]],
    'brown': [[139, 90, 43], [100, 65, 30], [120, 80, 50]],
    'beige': [[210, 190, 160], [195, 175, 145]],
    'green': [[50, 130, 60], [80, 120, 70]],
    'yellow': [[230, 200, 40], [200, 180, 50], [240, 220, 80]],
    'purple': [[100, 50, 150], [80, 40, 120], [130, 60, 160]],
  };

  Future<void> loadModel() async {
    if (_isLoaded) return;
    try {
      // Try multi-task model first
      try {
        _interpreter = await Interpreter.fromAsset(_multitaskModelAsset);
        _colLabels = await _loadLabels(_colLabelAsset);
        _seaLabels = await _loadLabels(_seaLabelAsset);
        _isMultitask = true;
        debugPrint('[ML] Loaded multi-task model (v5)');
      } catch (_) {
        // Fallback to legacy single-task model
        _interpreter = await Interpreter.fromAsset(_legacyModelAsset);
        _isMultitask = false;
        debugPrint('[ML] Loaded legacy model (v4)');
      }
      _catLabels = await _loadLabels(_catLabelAsset);
      _isLoaded = true;
    } catch (e) {
      _isLoaded = false;
      rethrow;
    }
  }

  Future<List<String>> _loadLabels(String asset) async {
    final data = await rootBundle.loadString(asset);
    return data.split('\n').map((l) => l.trim()).where((l) => l.isNotEmpty).toList();
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

    final resized = img.copyResize(originalImage, width: _inputSize, height: _inputSize);

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

    String category;
    double confidence;
    String color;
    String? season;

    if (_isMultitask) {
      // Multi-task: 3 outputs matched by shape
      final outputs = <int, Object>{};
      final outputTensors = _interpreter!.getOutputTensors();
      final outputMap = <String, int>{}; // 'category'|'color'|'season' → output index

      for (int i = 0; i < outputTensors.length; i++) {
        final shape = outputTensors[i].shape;
        final size = shape.last;
        if (size == _catLabels.length) {
          outputMap['category'] = i;
          outputs[i] = [List<double>.filled(size, 0)];
        } else if (size == _colLabels.length) {
          outputMap['color'] = i;
          outputs[i] = [List<double>.filled(size, 0)];
        } else if (size == _seaLabels.length) {
          outputMap['season'] = i;
          outputs[i] = [List<double>.filled(size, 0)];
        }
      }

      _interpreter!.runForMultipleInputs([input], outputs);

      // Category
      final catProbs = (outputs[outputMap['category']!]! as List<List<double>>)[0];
      final catResult = _argmax(catProbs);
      category = _catLabels[catResult.index];
      confidence = catResult.value;

      // Color — pixel-based is more reliable than ML for real-world photos
      // ML color is biased toward black (29% of training data)
      final pixelColor = _extractColor(originalImage);
      final colProbs = (outputs[outputMap['color']!]! as List<List<double>>)[0];
      final colResult = _argmax(colProbs);
      final mlColor = _colLabels[colResult.index];

      // Use pixel color as primary; ML color only if pixel returns gray (ambiguous)
      // and ML is confident (>60%) about a non-black color
      if (pixelColor == 'gray' && mlColor != 'black' && colResult.value > 0.6) {
        color = mlColor;
      } else {
        color = pixelColor;
      }

      // Season
      final seaProbs = (outputs[outputMap['season']!]! as List<List<double>>)[0];
      final seaResult = _argmax(seaProbs);
      season = _seaLabels[seaResult.index];

      stopwatch.stop();
      debugPrint('[ML] Multi-task inference in ${stopwatch.elapsedMilliseconds}ms — '
          '$category (${(confidence * 100).toStringAsFixed(1)}%), '
          'color: $color (pixel=$pixelColor, ml=$mlColor ${(colResult.value * 100).toStringAsFixed(0)}%), '
          'season: $season (${(seaResult.value * 100).toStringAsFixed(0)}%)');
    } else {
      // Legacy single-task: category only
      var output = [List<double>.filled(_catLabels.length, 0)];
      _interpreter!.run(input, output);

      final catResult = _argmax(output[0]);
      category = _catLabels[catResult.index];
      confidence = catResult.value;

      // Pixel-based color fallback
      color = _extractColor(originalImage);
      season = null;

      stopwatch.stop();
      debugPrint('[ML] Legacy inference in ${stopwatch.elapsedMilliseconds}ms — '
          '$category (${(confidence * 100).toStringAsFixed(1)}%), color: $color');
    }

    final style = _categoryStyles[category] ?? 'casual';

    return ClothingItem(
      category: category,
      color: color,
      style: style,
      season: season,
      confidence: confidence,
      imagePath: imagePath,
    );
  }

  _ArgmaxResult _argmax(List<double> probs) {
    int maxIdx = 0;
    double maxVal = probs[0];
    for (int i = 1; i < probs.length; i++) {
      if (probs[i] > maxVal) {
        maxVal = probs[i];
        maxIdx = i;
      }
    }
    return _ArgmaxResult(maxIdx, maxVal);
  }

  /// Pixel-based color extraction fallback (center 40% of image)
  String _extractColor(img.Image image) {
    final startX = (image.width * 0.3).toInt();
    final endX = (image.width * 0.7).toInt();
    final startY = (image.height * 0.3).toInt();
    final endY = (image.height * 0.7).toInt();

    int totalR = 0, totalG = 0, totalB = 0;
    int count = 0;

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

class _ArgmaxResult {
  final int index;
  final double value;
  const _ArgmaxResult(this.index, this.value);
}
