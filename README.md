# 선물 찾기 MCP 서버

온라인 선물 추천 + 근처 픽업 매장 검색을 한번에 제공하는 [PlayMCP](https://playmcp.kakao.com/) MCP 서버입니다.

## 데모 시나리오

> **유저:** "베프 생일인데 3만원대 감성 선물, 오늘 전달"

| 단계 | 툴 | 동작 |
|------|-----|------|
| ① | `quick_gift` | 네이버 쇼핑 실검색 TOP3 (가격·링크) |
| ② | `find_gift_pickup` | "강남역 꽃집" 근처 3곳 (카카오맵) |

## Tools

### `quick_gift`
네이버 [쇼핑 검색 API](https://developers.naver.com/docs/serviceapi/search/shopping/shopping.md)로 선물 상품을 추천합니다.

```json
{
  "query": "감성 선물",
  "min_price": 25000,
  "max_price": 35000,
  "limit": 3
}
```

### `find_gift_pickup`
카카오 [로컬 키워드 검색 API](https://developers.kakao.com/docs/ko/local/dev-guide)로 근처 픽업 매장을 찾습니다.

```json
{
  "query": "강남역 꽃집",
  "limit": 3
}
```

## API 키 발급

| 환경변수 | 발급처 | 용도 |
|----------|--------|------|
| `NAVER_CLIENT_ID` | [네이버 개발자센터](https://developers.naver.com) → 검색 API | quick_gift |
| `NAVER_CLIENT_SECRET` | ↑ | quick_gift |
| `KAKAO_REST_API_KEY` | [카카오 개발자](https://developers.kakao.com) → REST API 키 | find_gift_pickup |

## 로컬 실행

**Python 3.10+** 필요 (FastMCP 요구사항)

```bash
cp .env.example .env
# .env에 API 키 입력

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python server.py
```

- Health: `http://localhost:8000/health`
- MCP: `http://localhost:8000/`

## Docker 실행

```bash
cp .env.example .env
# .env에 API 키 입력

docker compose up --build
```

단독 빌드/실행:

```bash
docker build -t gift-find-mcp .
docker run --rm -p 8000:8000 --env-file .env gift-find-mcp
```

## Railway 배포

1. [Railway](https://railway.app) → **New Project** → **Deploy from GitHub repo**
2. 레포 `kakao_mcp_gift_find` 선택 (Dockerfile 자동 감지)
3. **Variables**에 환경변수 추가:

| 변수 | 필수 |
|------|------|
| `NAVER_CLIENT_ID` | ✅ |
| `NAVER_CLIENT_SECRET` | ✅ |
| `KAKAO_REST_API_KEY` | ✅ |

4. 배포 후 **Settings → Networking → Generate Domain** 으로 공개 URL 발급
5. Health check: `https://<your-domain>/health`
6. PlayMCP 등록 URL: `https://<your-domain>/`

> Railway는 `PORT`를 자동 주입합니다. Dockerfile/uvicorn이 이를 사용합니다.

## PlayMCP 등록

1. 클라우드(Railway, Render 등)에 배포
2. [PlayMCP 개발자 콘솔](https://playmcp.kakao.com/console)에서 서버 URL 등록
3. AI 채팅에서 테스트 → 심사 요청

## 카카오 선물하기 쇼핑 API에 대해

[카카오 Shopping Open API](https://shopping-developers.kakao.com/hc/ko/sections/4578925861775-%EC%84%A0%EB%AC%BC%ED%95%98%EA%B8%B0-%EC%83%81%ED%92%88-API-%EB%AA%85%EC%84%B8)는 **판매자(입점사)용** API입니다.

- 상품 등록/수정/심사, 브랜드·카테고리 조회 등
- 상품 조회는 **본인이 등록한 상품 ID**로만 가능
- 소비자용 "선물 추천/검색" API는 제공하지 않음

그래서 `quick_gift`는 네이버 쇼핑 검색 API를 사용합니다.

## 프로젝트 구조

```
├── Dockerfile
├── docker-compose.yml
├── server.py              # FastMCP + FastAPI 엔트리포인트
├── src/
│   ├── naver_shopping.py  # quick_gift API 클라이언트
│   ├── kakao_local.py     # find_gift_pickup API 클라이언트
│   └── mcp_tools_schema.py
├── requirements.txt
└── .env.example
```
