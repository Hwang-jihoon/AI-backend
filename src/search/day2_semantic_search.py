import time
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

def main():
    # 1. 모델 로드 및 ES 연결
    print("[1/4] 한국어 임베딩 모델 로드 중 (최초 실행 시 다운로드 약 1~2분 소요)...")
    model = SentenceTransformer('jhgan/ko-sroberta-multitask')
    
    es = Elasticsearch("http://localhost:9200")
    index_name = "recipe_data_vector"

    # 2. Vector 필드가 포함된 인덱스 맵핑
    mapping = {
        "settings": {
            "analysis": {
                "analyzer": {
                    "nori_analyzer": {
                        "type": "custom",
                        "tokenizer": "nori_tokenizer"
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "title": {"type": "text", "analyzer": "nori_analyzer"},
                "content": {"type": "text", "analyzer": "nori_analyzer"},
                "content_vector": {
                    "type": "dense_vector",
                    "dims": 768,
                    "index": True,
                    "similarity": "cosine"
                }
            }
        }
    }

    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
    es.indices.create(index=index_name, body=mapping)
    print(f"[2/4] '{index_name}' 인덱스 생성 완료 (Vector 필드 포함)")

    # 3. 데이터 임베딩 및 적재
    docs = [
        {"title": "김치찌개 레시피", "content": "묵은지와 돼지고기를 넣고 푹 끓인 깊은 맛의 김치찌개입니다."},
        {"title": "된장찌개 레시피", "content": "두부와 애호박이 듬뿍 들어간 구수한 된장찌개 레시피."},
        {"title": "돼지고기 볶음", "content": "매콤달콤한 양념에 재운 돼지고기 앞다리살 볶음."}
    ]

    for i, doc in enumerate(docs):
        vector = model.encode(doc["content"]).tolist()
        doc["content_vector"] = vector
        es.index(index=index_name, id=i, document=doc)
    
    es.indices.refresh(index=index_name)
    print(f"[3/4] 샘플 문서 {len(docs)}건 벡터화 및 적재 완료")

    # 4. 벡터 검색(Semantic Search) 테스트
    search_query = "얼큰한 고기 찌개 알려줘"
    print(f"\n[4/4] 검색 질의: '{search_query}'")
    
    query_vector = model.encode(search_query).tolist()

    response = es.search(
        index=index_name,
        knn={
            "field": "content_vector",
            "query_vector": query_vector,
            "k": 3,
            "num_candidates": 10
        }
    )

    print("\n" + "=" * 50)
    print("벡터 검색 결과 (Cosine Similarity 순)")
    print("=" * 50)
    for hit in response["hits"]["hits"]:
        score = hit["_score"]
        title = hit["_source"]["title"]
        content = hit["_source"]["content"]
        print(f"• [Score: {score:.4f}] {title}")
        print(f"  내용: {content}\n")

if __name__ == "__main__":
    main()
