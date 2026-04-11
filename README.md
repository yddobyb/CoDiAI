# CoDi AI

CoDi AI is a Flutter app that analyzes a clothing photo on-device, builds outfit recommendations, and connects the result to a broader fashion workflow with auth, closet history, and product browsing.

The default `main` branch is the expanded product branch. If you want the original course MVP with the simpler 3-screen flow and 9-category model demo, use the `assignment` branch.

## What the app does

- Runs a TFLite clothing model directly on-device
- Predicts clothing category, color, and season with a multi-task model
- Falls back to a legacy category-only model if the multi-task asset is unavailable
- Generates outfit recommendations with an explainable rule-based engine
- Supports auth, closet/history flows, daily outfits, and shop/product browsing
- Adds Gemini-powered style tips as an optional layer

## Current stack

| Layer | Technology |
| --- | --- |
| App | Flutter, Dart |
| State / Routing | Riverpod, GoRouter |
| ML inference | `tflite_flutter`, `image` |
| Backend | Supabase Auth + Postgres |
| LLM | Gemini API |
| Training | Python, TensorFlow / Keras, MobileNetV2 |

## Branches

- `main`: current app branch with auth, closet, history, shop, daily outfit, and multi-task model support
- `assignment`: original COMP4949 assignment branch with the simpler MVP/demo flow

## ML summary

- Current on-device asset: multi-task TFLite model
- Category labels: 15
- Color labels: 11 ML labels plus pixel-based fallback logic
- Season labels: 4
- Legacy fallback asset: category-only TFLite model

The current mobile pipeline is implemented in [ml_service.dart](app/lib/services/ml_service.dart), and the recommendation engine lives in [recommendation_service.dart](app/lib/services/recommendation_service.dart).

## Repository structure

```text
codi/
├── app/
│   ├── assets/                     # TFLite assets and labels
│   ├── lib/
│   │   ├── core/                   # config, theme, router, errors
│   │   ├── features/               # home, analysis, auth, closet, history, profile, shop
│   │   ├── models/                 # shared app models
│   │   ├── providers/              # Riverpod providers
│   │   ├── services/               # ML, recommendation, auth, profile, product logic
│   │   └── widgets/                # shared UI building blocks
│   └── test/                       # Flutter tests
├── model/
│   ├── notebooks/                  # notebook-based experimentation
│   ├── train.py                    # original 9-category training pipeline
│   ├── train_v4_expanded.py        # expanded category pipeline
│   ├── train_v5_multitask.py       # current multi-task training pipeline
│   ├── finetune_v3.py              # real-world fine-tuning script
│   └── finetune_realworld.py       # extra domain-gap fine-tuning work
└── .github/workflows/ci.yml        # analyze + test workflow
```

## Local setup

### Prerequisites

- Flutter 3.35+
- Xcode or Android SDK
- Python 3.13+ if you want to run training scripts

### 1. Install Flutter dependencies

```bash
cd app
flutter pub get
```

### 2. Create local config files

These files are intentionally gitignored.

Create `app/lib/core/config/supabase_config.dart`:

```dart
const supabaseUrl = 'https://YOUR_PROJECT.supabase.co';
const supabaseAnonKey = 'YOUR_SUPABASE_ANON_KEY';
```

Create `app/lib/core/config/api_keys.dart`:

```dart
const geminiApiKey = '';
```

Create `app/lib/core/config/oauth_config.dart`:

```dart
const googleWebClientId = '';
const googleIosClientId = '';
```

Notes:

- A valid Supabase project is required to run the full app.
- Gemini is optional. If `geminiApiKey` is empty, the app still works without style-tip generation.
- Google / Apple sign-in setup is optional for local development, but the file must exist.

### 3. Run the app

```bash
cd app
flutter run
```

## Training scripts

From the `model/` directory:

```bash
source venv/bin/activate
python train_v5_multitask.py
```

Useful variants:

- `python train.py`: original assignment-era 9-category model
- `python train_v4_expanded.py`: expanded category model
- `python finetune_v3.py`: fine-tuning with additional real-world photos

The heavy training artifacts and datasets are not committed to this repository.

## Notes for reviewers

- `main` is the best branch to review for the current app architecture.
- `assignment` is useful if you want to see the original portfolio / course submission version.
- CI creates blank local config stubs so analyze and tests can run without private keys.

## Author

Young Bin Park
