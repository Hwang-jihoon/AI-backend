import time
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

def get_rrf_score(rank, k=60):
    """RRF 공식: 1 / (k + rank)"""
    return 1.0 / (k + rank)

def main():
    print("[1/3] 모델 로드 및 ES 연결 중...")
    model = SentenceTransformer('jhgan/ko-sroberta-multitask')
    es = Elasticsearch("http://localhost:9200")
    index_name = "recipe_data_vector" # Day 2에서 만든 인덱스 재사용

    search_query = "얼큰한 돼지고기 찌개"
    print(f"\n[2/3] 검색 질의: '{search_query}'")
    
    # 1. Lexical Search (BM25)
    lexical_response = es.search(
        index=index_name,
        query={
            "match": {
                "content": search_query
            }
        },
        size=5
    )
    
    # 2. Semantic Search (Vector K-NN)
    query_vector = model.encode(search_query).tolist()
    vector_response = es.search(
        index=index_name,
        knn={
            "field": "content_vector",
            "query_vector": query_vector,
            "k": 5,
            "num_candidates": 10
        },
        size=5
    )

    # 3. RRF (Reciprocal Rank Fusion) 적용
    print("[3/3] RRF 융합 점수 계산 중...\n")
    rrf_scores = {}
    
    # BM25 결과 순위 기록
    for rank, hit in enumerate(lexical_response["hits"]["hits"], start=1):
        doc_id = hit["_id"]
        if doc_id not in rrf_scores:
            rrf_scores[doc_id] = {"score": 0.0, "source": hit["_source"]}
        rrf_scores[doc_id]["score"] += get_rrf_score(rank)

    # Vector 결과 순위 기록 및 합산
    for rank, hit in enumerate(vector_response["hits"]["hits"], start=1):
        doc_id = hit["_id"]
        if doc_id not in rrf_scores:
            rrf_scores[doc_id] = {"score": 0.0, "source": hit["_source"]}
        rrf_scores[doc_id]["score"] += get_rrf_score(rank)

    # RRF 점수 기준으로 내림차순 정렬
    sorted_results = sorted(rrf_scores.items(), key=lambda x: x[1]["score"], reverse=True)

    print("=" * 50)
    print("하이브리드 검색 결과 (RRF Score 순)")
    print("=" * 50)
    for doc_id, data in sorted_results:
        score = data["score"]
        title = data["source"]["title"]
        content = data["source"]["content"]
        print(f"• [RRF Score: {score:.4f}] {title}")
        print(f"  내용: {content}\n")

if __name__ == "__main__":
    main()
