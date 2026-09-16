# Day 2: 임베딩 모델을 활용한 벡터 검색(Semantic Search) 파이프라인

## 1. 학습 목표
- `sentence-transformers`를 활용해 텍스트 데이터를 768차원 벡터로 변환(Embedding).
- Elasticsearch의 `dense_vector` 필드와 K-NN 알고리즘을 활용한 의미 기반 검색 구현.

## 2. 주요 구현 내용
- 사용 모델: `jhgan/ko-sroberta-multitask` (한국어 특화 임베딩 모델)
- `src/search/day2_semantic_search.py`: "얼큰한 고기 찌개 알려줘"라는 질의어 검색 시, BM25로는 매칭되지 않는 "매콤달콤한", "찌개" 등의 문맥적 의미를 파악하여 연관 문서를 찾아냄.

## 3. 실행 가이드
```bash
# 1. 패키지 설치
pip install -r requirements.txt

# 2. 벡터 검색 스크립트 실행
python src/search/day2_semantic_search.py
