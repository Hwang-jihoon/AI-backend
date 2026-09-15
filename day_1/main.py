import time
from elasticsearch import Elasticsearch

def main():
    # 1. Elasticsearch 클라이언트 연결
    es = Elasticsearch("http://localhost:9200")

    # 연결 확인
    try:
        info = es.info()
        print(f"[1/4] Elasticsearch 연결 성공: {info['version']['number']}")
    except Exception as e:
        print(f"연결 실패: Docker 컨테이너가 정상 실행 중인지 확인하세요. ({e})")
        return

    index_name = "recipe_data"

    # 2. Nori 분석기가 적용된 인덱스 맵핑 정의
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
                "content": {"type": "text", "analyzer": "nori_analyzer"}
            }
        }
    }

    # 기존 인덱스가 있다면 삭제 후 생성
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
        print(f"기존 인덱스 '{index_name}' 삭제 완료")

    es.indices.create(index=index_name, body=mapping)
    print(f"[2/4] '{index_name}' 인덱스 생성 완료 (Nori Analyzer 적용)")

    # 3. 테스트용 샘플 문서 적재
    docs = [
        {
            "title": "김치찌개 레시피",
            "content": "묵은지와 돼지고기를 넣고 푹 끓인 깊은 맛의 김치찌개입니다."
        },
        {
            "title": "된장찌개 레시피",
            "content": "두부와 애호박이 듬뿍 들어간 구수한 된장찌개 레시피."
        },
        {
            "title": "돼지고기 볶음",
            "content": "매콤달콤한 양념에 재운 돼지고기 앞다리살 볶음."
        }
    ]

    for i, doc in enumerate(docs):
        es.index(index=index_name, id=i, document=doc)
    
    # 즉시 검색 가능하도록 인덱스 refresh
    es.indices.refresh(index=index_name)
    print(f"[3/4] 샘플 문서 {len(docs)}건 적재 완료")

    # 4. BM25 키워드 검색 테스트
    search_query = "돼지고기 듬뿍 김치찌개"
    print(f"\n[4/4] 검색 질의: '{search_query}'")

    response = es.search(
        index=index_name,
        query={
            "match": {
                "content": search_query
            }
        }
    )

    print("\n" + "=" * 50)
    print("검색 결과 (BM25 Score 순)")
    print("=" * 50)
    for hit in response["hits"]["hits"]:
        score = hit["_score"]
        title = hit["_source"]["title"]
        content = hit["_source"]["content"]
        print(f"• [Score: {score:.4f}] {title}")
        print(f"  내용: {content}\n")

if __name__ == "__main__":
    main()
