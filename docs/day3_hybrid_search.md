# Day 3: 하이브리드 검색 (Hybrid Search) 및 RRF 기반 순위 융합

## 1. 학습 목표
- 키워드 매칭(BM25)과 문맥 매칭(Vector)의 장점을 결합한 하이브리드 검색 파이프라인 구축.
- `RRF (Reciprocal Rank Fusion)` 알고리즘을 파이썬 레벨에서 구현하여 서로 다른 스케일의 점수(Score)를 가진 두 검색 결과를 공정하게 병합.

## 2. 주요 구현 내용
- `src/search/day3_hybrid_search.py`: 동일한 질의어("얼큰한 돼지고기 찌개")로 Lexical 쿼리와 Semantic 쿼리를 각각 Elasticsearch에 요청.
- **RRF 공식 적용**: $Score = \frac{1}{k + rank}$ (일반적으로 k=60 사용). 각 검색 결과의 순위(rank)를 기반으로 점수를 역산하여 합산한 뒤 최종 랭킹 도출.
- 특정 키워드("돼지고기")가 포함되면서도 문맥상 일치하는 결과("김치찌개")가 압도적으로 최상단에 노출됨을 확인.

## 3. 실행 가이드
```bash
python src/search/day3_hybrid_search.py
