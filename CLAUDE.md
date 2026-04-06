# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Fashion Codi AI** — 사용자가 옷 사진을 업로드하면 자체 ML 모델이 의류를 분석하고, 코디를 추천하며, 비슷한 상품 탐색과 쇼핑까지 연결하는 패션 AI 플랫폼.

핵심: 자체 학습한 CV 모델이 서비스의 출발점. 타겟: 캐나다 여성 미니멀 / 대학생 데일리룩.

## Target Market

- **지역**: 캐나다 (CAD 기준)
- **세그먼트**: 여성 미니멀 / 대학생 데일리룩
- **주요 브랜드**: Aritzia (TNA, Wilfred, Babaton, Denim Forum), Garage, Dynamite, Oak + Fort, Simons, Frank and Oak, Roots, Lululemon, Kotn, RW&Co
- **국제 브랜드 (캐나다 입점)**: H&M, Zara, Uniqlo, COS
- **가격대**: $15~$350 CAD (대학생 접근 가능한 가격대)
- **제휴 프로그램**: Amazon Associates Canada, Rakuten, SSENSE affiliate (Phase B)

## Current Stage

**Stage 2 (상업화)** 진행 중. Stage 1 MVP는 `assignment` 브랜치에 보존.

- 2-1: 리팩토링 + 인프라 (Riverpod, GoRouter, Supabase)
- 2-2: 사용자 기능 + 옷장 (Auth, Closet, History)
- 2-3: ML 고도화 (카테고리 확장, 속성 인식, 이미지 임베딩)
- 2-4: 쇼핑 통합 + 수익화 (유사 상품 검색, 제휴 링크)

## Tech Stack

| 영역 | 기술 |
|------|------|
| ML 학습 | Python 3.13 + TensorFlow/Keras + MobileNetV2 (Transfer Learning) |
| 모델 배포 | TFLite (온디바이스, float16, 4.6MB) |
| 앱 | Flutter 3.35 + Dart |
| 상태관리 | Riverpod |
| 라우팅 | GoRouter |
| 백엔드 | Supabase (Auth, PostgreSQL, Storage, Edge Functions) |
| 벡터 검색 | Supabase pgvector |
| LLM | Gemini API (HTTP REST, gemini-2.5-flash) |
| CI/CD | GitHub Actions |

## Project Structure

```
codi/
├── model/                          # Python ML 파이프라인
│   ├── notebooks/                  # Jupyter 학습 노트북 (01-05)
│   ├── data/                       # 데이터셋 (git 미추적)
│   ├── saved_model/                # 학습된 모델 (git 미추적)
│   ├── tflite/                     # 변환된 모델 (git 미추적)
│   └── venv/                       # Python 가상환경 (git 미추적)
├── app/                            # Flutter 앱
│   └── lib/
│       ├── core/                   # config, errors, theme, router
│       ├── features/               # 화면별 기능 모듈
│       │   ├── home/               # 홈 (사진 업로드)
│       │   ├── analysis/           # ML 분석
│       │   ├── recommendation/     # 코디 추천
│       │   ├── closet/             # 내 옷장
│       │   ├── auth/               # 로그인/회원가입
│       │   ├── profile/            # 프로필/설정
│       │   └── shop/               # 쇼핑 탐색
│       ├── models/                 # 공유 데이터 모델
│       ├── services/               # 비즈니스 로직
│       ├── providers/              # Riverpod Provider
│       └── widgets/                # 공유 위젯
├── plan.md                         # 상세 개발 계획
└── CLAUDE.md
```

## Commands

### Python ML (model/)
```bash
source model/venv/bin/activate
jupyter notebook model/notebooks/
# 패키지: tensorflow, keras, numpy, pandas, matplotlib, pillow, jupyter, kagglehub
```

### Flutter App (app/)
```bash
cd app && flutter pub get
cd app && flutter run
cd app && flutter build ios
cd app && flutter build apk
# 패키지: tflite_flutter, image_picker, image, http, flutter_riverpod, go_router, supabase_flutter
```

## ML Model

- **아키텍처**: MobileNetV2 + Multi-Task Heads (GAP → Dense(256) → Category/Color/Season heads)
- **카테고리**: 15개 (Boots, Coat, Dress, Flats, Heels, Hoodie, Jacket, Jeans, Pants, Shirt, Shorts, Skirt, Sneakers, Sweater, T-shirt)
- **색상**: ML 11색 (beige, black, blue, brown, gray, green, navy, pink, red, white, yellow) + 픽셀 감지 12색 (purple 포함)
- **계절**: 4개 (spring, summer, fall, winter)
- **스타일**: casual, formal, sporty
- **성능**: Category 89.73%, Color 71.69%, Season 72.88%, TFLite 5.0MB
- **알려진 한계**: Flats↔Heels 혼동, navy→black 혼동, 소수 클래스(Hoodie/Jacket) 정확도 낮음

## Supabase DB Schema

```sql
profiles (id, email, nickname, style_preference, is_premium, created_at)
closet_items (id, user_id, image_url, category, color, style, confidence, created_at)
outfit_history (id, user_id, user_item_id, recommendations_json, liked, created_at)
products (id, name, brand, category, color, style, price, image_url, affiliate_url, embedding vector(512), created_at)
click_events (id, user_id, product_id, event_type, created_at)
daily_usage (id, user_id, usage_date, analysis_count, UNIQUE(user_id, usage_date))
```

## App Flow

1. 사용자가 옷 사진 업로드 (갤러리/카메라)
2. TFLite 모델이 온디바이스에서 카테고리/색상/계절 예측 (멀티태스크)
3. 색상 추출 (픽셀 기반 primary + ML fallback) + 스타일 태그
4. 개인화 프로파일 빌드 (옷장 빈도 + 피드백 학습 + 프로필 선호도)
5. 추천 엔진이 코디 조합 3개 생성 (카테고리 40% + 색상 35% + 스타일 25% + 개인화 ±14%)
6. Gemini API가 AI Style Tip 생성
7. (Stage 2-4) 유사 상품 검색 (이미지 임베딩 + pgvector)
8. 결과 화면에서 추천 코디 + 유사 상품 + 구매 링크 표시

## Recommendation Logic

- **카테고리 궁합**: 상의×하의, 하의×신발, 상의×신발 매트릭스
- **색상 조화**: 3단계 중립색 체계 (pure neutral / fashion neutral / chromatic), 보색 0.80, 동색 0.70
- **스타일 일관성**: 동일 1.0, sporty+formal 0.35
- **기본 점수** = 카테고리(0.4) + 색상(0.35) + 스타일(0.25)
- **개인화**: 프로필 스타일(+5%) + 옷장 색상 친밀도(+3%) + 옷장 스타일 친밀도(+2%) + 피드백 바이어스(±4%)

## Key Config Files (gitignored)

- `app/lib/core/config/api_keys.dart` — Gemini API 키
- `app/lib/core/config/supabase_config.dart` — Supabase URL + Anon Key

## Key Risks

- 카테고리 확장 시 정확도 하락 → 단계적 확장, 충분한 데이터 확보 후 추가
- 상품 DB 커버리지 부족 → 여성 미니멀 세그먼트 먼저 깊이 있게
- Shirt↔Jacket 혼동 → 실사진 데이터 추가 수집 + fine-tuning
