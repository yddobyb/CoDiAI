# Fashion Codi AI

A Flutter-based fashion AI app that uses a custom-trained MobileNetV2 model to classify clothing items on-device and recommend outfit combinations with AI-powered style tips.

**COMP4949 Assignment 2** — "Build an app or game with a machine learning model (that you built) embedded in the app or game."

## How It Works

1. **Upload** a clothing photo (gallery or camera)
2. **On-device ML** classifies the item (category, color, style) using TFLite
3. **Recommendation engine** generates 3 outfit combinations using rule-based scoring
4. **Gemini AI** provides natural language style tips for each recommendation

## Demo

> Video link: [TBD]

## Key Features

- **Custom ML Model**: MobileNetV2 Transfer Learning, trained on 21,338 images, 9 clothing categories
- **On-Device Inference**: TFLite model runs locally (~300ms per prediction)
- **Smart Recommendations**: Category compatibility + color harmony + style consistency scoring
- **AI Style Tips**: Gemini 2.5 Flash generates contextual fashion advice
- **Clean UI**: Material 3 design with 3 screens (Home, Analysis, Outfit Ideas)

## Model Performance

| Metric | Value |
|--------|-------|
| Architecture | MobileNetV2 + Custom Head |
| Training Data | 21,338 images (Kaggle Fashion Product Images) |
| Categories | 9 (T-shirt, Shirt, Hoodie, Jacket, Pants, Jeans, Dress, Sneakers, Boots) |
| Val Accuracy | 91.07% (after v3 fine-tuning) |
| Test Accuracy | 90.75% |
| TFLite Size | 4.6 MB (float16 quantization, 79.7% reduction) |
| Inference Time | ~276-369ms (iPhone 17 Pro simulator) |

## Tech Stack

| Layer | Technology |
|-------|-----------|
| ML Training | Python 3.13, TensorFlow/Keras, MobileNetV2 |
| Model Format | .keras -> .tflite (float16 quantized) |
| App | Flutter 3.35, Dart |
| On-Device ML | tflite_flutter |
| Color Detection | Dart `image` package (multi-reference RGB matching) |
| Recommendation | Rule-based scoring (Dart) |
| LLM | Gemini API (HTTP REST, gemini-2.5-flash) |

## Project Structure

```
ml2/
├── model/                          # ML pipeline (Python)
│   ├── notebooks/                  # Jupyter notebooks (01-05)
│   │   ├── 01_data_exploration     # Dataset EDA
│   │   ├── 02_preprocessing        # Data cleaning & augmentation
│   │   ├── 03_model_training       # MobileNetV2 training (Phase 1 + 2)
│   │   ├── 04_evaluation           # Test metrics & confusion matrix
│   │   └── 05_tflite_conversion    # Keras -> TFLite conversion
│   ├── train.py                    # Training script (v1)
│   ├── finetune_v3.py              # Fine-tuning with real-world photos
│   ├── data/                       # Datasets & labels
│   ├── saved_model/                # Trained models (.keras)
│   └── tflite/                     # Converted models (.tflite)
├── app/                            # Flutter app
│   ├── lib/
│   │   ├── config/                 # API keys (gitignored)
│   │   ├── models/                 # Data models
│   │   │   ├── clothing_item.dart
│   │   │   └── outfit_recommendation.dart
│   │   ├── services/               # Business logic
│   │   │   ├── ml_service.dart     # TFLite inference + color extraction
│   │   │   ├── recommendation_service.dart  # Outfit scoring engine
│   │   │   └── llm_service.dart    # Gemini API integration
│   │   ├── screens/                # UI screens
│   │   │   ├── home_screen.dart    # Photo upload
│   │   │   ├── upload_screen.dart  # Analysis & results
│   │   │   └── result_screen.dart  # Outfit recommendations
│   │   └── widgets/                # Reusable components
│   └── assets/                     # TFLite model + labels
└── plan.md                         # Development plan & progress
```

## Getting Started

### Prerequisites

- Flutter 3.35+
- Xcode (for iOS) or Android SDK
- Python 3.13+ (for model training only)

### Run the App

```bash
cd app
flutter pub get
flutter run
```

### Gemini API Setup (for AI Style Tips)

1. Get an API key from [Google AI Studio](https://aistudio.google.com/apikey)
2. Create `app/lib/config/api_keys.dart`:
```dart
const geminiApiKey = 'YOUR_API_KEY_HERE';
```

> The app works without the API key -- AI Style Tips will simply not appear.

### Train the Model (Optional)

```bash
cd model
source venv/bin/activate
python train.py          # Full training
python finetune_v3.py    # Fine-tune with real-world images
```

## Recommendation Logic

The outfit scoring engine combines three factors:

- **Category Compatibility (40%)**: Pre-defined compatibility matrix for top/bottom/shoes combinations
- **Color Harmony (35%)**: Neutral+chromatic pairing, complementary colors, monochrome rules
- **Style Consistency (25%)**: Matching casual/formal/sporty styles across items

Final score = category(0.4) + color(0.35) + style(0.25)

## Known Limitations

- **Shirt vs Jacket**: Dress shirts are sometimes classified as Jacket (60.3% confidence) due to visual similarity in the training data
- **LLM Response Time**: AI Style Tips take ~3-4 seconds to generate (recommendations appear instantly)
- **Color Detection**: Works best with solid-colored items; patterns may produce unexpected color results

## ML Training Pipeline

1. **Data Collection**: Kaggle Fashion Product Images (44K images) + Clothing Dataset Full (1.3K supplementary)
2. **Preprocessing**: 224x224 resize, MobileNetV2 normalization, stratified split (70/15/15)
3. **Augmentation**: Horizontal flip, brightness (+-0.15), contrast (0.8-1.2), random crop
4. **Phase 1**: Backbone frozen, classification head only -- val_accuracy 87.82%
5. **Phase 2**: Last 30 layers unfrozen, lr=1e-5 -- val_accuracy 90.32%
6. **Phase 3 (v3)**: Fine-tuned with 130 real-world shirt photos -- val_accuracy 91.07%
7. **Conversion**: Keras -> TFLite (float16), accuracy diff 0.09%

## Author

Young Bin Park -- COMP4949, BCIT
