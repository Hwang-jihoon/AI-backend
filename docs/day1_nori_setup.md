# Day 1: Elasticsearch 기반 텍스트 검색(Lexical) 고도화

## 1. 학습 목표
- 한국어 RAG 시스템 구축을 위해 Elasticsearch에 Nori 형태소 분석기 플러그인 적용.
- 사용자 정의 인덱스 맵핑(Mapping)을 통해 BM25 기반 키워드 검색 정확도 향상.

## 2. 주요 구현 내용
- `docker-compose.yml`: 단일 노드(Single-node) Elasticsearch 컨테이너 구성 및 메모리 튜닝.
- `src/search/day1_lexical_search.py`: Nori Analyzer가 적용된 `recipe_data` 인덱스 생성 및 샘플 데이터 색인. "돼지고기 듬뿍 김치찌개" 검색 시 형태소가 분리되어 연관 문서가 스코어링됨을 확인.

## 3. 트러블슈팅 (Troubleshooting) 🚨
### 이슈: 도커 컨테이너 내부 플러그인 설치 시 네트워크 에러
Codespaces 환경에서 Elasticsearch 컨테이너를 띄우고 Nori 플러그인을 설치(`bin/elasticsearch-plugin install`)하는 과정에서 아래와 같은 DNS/네트워크 에러 발생.
> `Exception in thread "main" java.net.UnknownHostException: artifacts.elastic.co`

### 원인
클라우드 IDE(Codespaces) 환경에서 도커 컨테이너 구동 시 일시적인 네트워크 격리 현상으로 인해 외부 플러그인 다운로드 서버를 찾지 못함.

### 해결: 오프라인(수동) 다운로드 및 주입 방식으로 우회
인터넷이 연결된 호스트(Codespaces 터미널)에서 플러그인 zip 파일을 먼저 다운로드한 뒤, 컨테이너 내부로 복사하여 로컬 파일로 설치 진행.

```bash
# 1. 호스트에서 플러그인 다운로드
curl -L -o nori.zip [https://artifacts.elastic.co/downloads/elasticsearch-plugins/analysis-nori/analysis-nori-8.12.0.zip](https://artifacts.elastic.co/downloads/elasticsearch-plugins/analysis-nori/analysis-nori-8.12.0.zip)

# 2. 컨테이너 내부로 압축 파일 복사
docker cp nori.zip es-nori:/tmp/

# 3. 로컬 경로를 참조하여 플러그인 오프라인 설치
docker exec -it es-nori bin/elasticsearch-plugin install --batch file:///tmp/nori.zip

## 4. 실행 가이드 및 테스트 결과

### 실행 방법
프로젝트 루트(최상단) 디렉토리에서 다음 순서대로 명령어를 실행합니다.

**1. Elasticsearch 인프라 구동 (Docker)**
컨테이너를 백그라운드에서 실행하고, Nori 플러그인이 로드될 때까지 약 15~20초 정도 대기합니다.

```bash
docker-compose up -d
```

**2. 파이썬 의존성 설치

```bash
pip install -r requirements.txt
```

**3. 검색 로직 실행
엔진이 완전히 준비되면 텍스트 검색 스크립트를 실행합니다.

```bash
python src/search/day1_lexical_search.py
```

