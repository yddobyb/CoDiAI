import 'dart:io';
import 'package:flutter/material.dart';
import '../models/clothing_item.dart';
import '../services/ml_service.dart';
import '../widgets/clothing_tag_chip.dart';
import '../widgets/confidence_bar.dart';
import 'result_screen.dart';

class UploadScreen extends StatefulWidget {
  final String imagePath;

  const UploadScreen({super.key, required this.imagePath});

  @override
  State<UploadScreen> createState() => _UploadScreenState();
}

class _UploadScreenState extends State<UploadScreen> {
  final MlService _mlService = MlService();
  ClothingItem? _result;
  bool _isAnalyzing = false;
  bool _isModelLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadModel();
  }

  Future<void> _loadModel() async {
    try {
      await _mlService.loadModel();
      if (mounted) setState(() => _isModelLoading = false);
    } catch (e) {
      if (mounted) {
        setState(() {
          _isModelLoading = false;
          _error = 'Failed to load ML model: $e';
        });
      }
    }
  }

  Future<void> _analyze() async {
    setState(() {
      _isAnalyzing = true;
      _error = null;
    });

    try {
      final result = await _mlService.predict(widget.imagePath);
      if (mounted) setState(() => _result = result);
    } catch (e) {
      if (mounted) setState(() => _error = 'Analysis failed: $e');
    } finally {
      if (mounted) setState(() => _isAnalyzing = false);
    }
  }

  @override
  void dispose() {
    _mlService.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: Text(_result == null ? 'Analyze Item' : 'Analysis Result'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Image preview
            ClipRRect(
              borderRadius: BorderRadius.circular(16),
              child: AspectRatio(
                aspectRatio: 1,
                child: Image.file(
                  File(widget.imagePath),
                  fit: BoxFit.cover,
                ),
              ),
            ),
            const SizedBox(height: 20),

            // Error display
            if (_error != null) ...[
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.red.shade50,
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: Colors.red.shade200),
                ),
                child: Row(
                  children: [
                    Icon(Icons.error_outline, color: Colors.red.shade700, size: 20),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        _error!,
                        style: TextStyle(color: Colors.red.shade700, fontSize: 13),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 12),
              SizedBox(
                height: 48,
                child: OutlinedButton.icon(
                  onPressed: () {
                    setState(() => _error = null);
                    _analyze();
                  },
                  icon: const Icon(Icons.refresh_rounded, size: 20),
                  label: const Text('Retry Analysis'),
                  style: OutlinedButton.styleFrom(
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(14),
                    ),
                  ),
                ),
              ),
            ],

            // Analysis results
            if (_result != null) ...[
              _buildResultSection(theme),
              const SizedBox(height: 20),
              SizedBox(
                height: 52,
                child: FilledButton.icon(
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (_) => ResultScreen(userItem: _result!),
                      ),
                    );
                  },
                  icon: const Icon(Icons.style_rounded),
                  label: const Text(
                    'Get Outfit Suggestions',
                    style: TextStyle(fontSize: 16),
                  ),
                  style: FilledButton.styleFrom(
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(14),
                    ),
                  ),
                ),
              ),
            ],

            // Analyze button (before analysis)
            if (_result == null && _error == null) ...[
              const SizedBox(height: 4),
              SizedBox(
                height: 52,
                child: FilledButton.icon(
                  onPressed: (_isAnalyzing || _isModelLoading) ? null : _analyze,
                  icon: _isAnalyzing || _isModelLoading
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            color: Colors.white,
                          ),
                        )
                      : const Icon(Icons.search_rounded),
                  label: Text(
                    _isModelLoading
                        ? 'Loading Model...'
                        : _isAnalyzing
                            ? 'Analyzing...'
                            : 'Analyze Clothing',
                    style: const TextStyle(fontSize: 16),
                  ),
                  style: FilledButton.styleFrom(
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(14),
                    ),
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildResultSection(ThemeData theme) {
    final item = _result!;
    return Card(
      elevation: 1,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Detection Result',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),

            // Tags
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                ClothingTagChip(
                  label: item.category,
                  icon: Icons.checkroom,
                  backgroundColor: theme.colorScheme.primaryContainer,
                ),
                ClothingTagChip(
                  label: item.color,
                  backgroundColor: item.colorValue.withValues(alpha: 0.25),
                ),
                ClothingTagChip(
                  label: item.style,
                  icon: Icons.style,
                  backgroundColor: theme.colorScheme.tertiaryContainer,
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Confidence bar
            ConfidenceBar(confidence: item.confidence),

            // Low confidence warning
            if (item.confidence < 0.6) ...[
              const SizedBox(height: 8),
              Row(
                children: [
                  Icon(Icons.warning_amber_rounded,
                      size: 16, color: Colors.orange.shade700),
                  const SizedBox(width: 4),
                  Text(
                    'Low confidence — result may be inaccurate',
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.orange.shade700,
                    ),
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }
}
