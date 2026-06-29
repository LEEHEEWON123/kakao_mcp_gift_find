MCP_SERVER_INSTRUCTIONS = """\
선물 찾기 MCP 서버입니다. 사용자가 선물, 생일, 기념일, 당일 전달 등을 언급하면 아래 도구를 활용하세요.

1. quick_gift — 온라인 선물 추천 (네이버 쇼핑 실검색 TOP3, 가격·링크)
2. find_gift_pickup — 받는 사람 주소 기준 픽업 매장 검색 (거리·카카오맵)

데모 시나리오:
유저: "베프 생일 3만원대 감성 선물, 걔 집 강남역 근처, 오늘 전달"
→ quick_gift(query="감성 선물", max_price=35000, min_price=25000)
→ find_gift_pickup(address="서울 강남구 강남역", store_query="꽃집")
"""


def get_mcp_tools_list() -> list[dict]:
    return [
        {
            "name": "quick_gift",
            "description": (
                "네이버 쇼핑 실검색으로 선물 상품 TOP3를 추천합니다. "
                "가격대 필터링이 가능합니다. "
                "트리거: 온라인 선물, 쇼핑, 가격대 추천, 네이버 검색"
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "검색 키워드 (예: '감성 선물', '생일 케이크')",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "추천 개수 (기본 3)",
                        "default": 3,
                    },
                    "min_price": {
                        "type": "integer",
                        "description": "최소 가격 (원, 예: 25000)",
                    },
                    "max_price": {
                        "type": "integer",
                        "description": "최대 가격 (원, 예: 35000)",
                    },
                },
                "required": ["query"],
            },
        },
        {
            "name": "find_gift_pickup",
            "description": (
                "받는 사람 집 주소(또는 랜드마크) 기준으로 픽업 가능한 오프라인 매장을 찾습니다. "
                "집에서 거리, 매장명, 주소, 전화, 카카오맵 링크를 반환합니다. "
                "트리거: 오늘 전달, 당일 픽업, 집 근처 매장, 픽업"
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "address": {
                        "type": "string",
                        "description": "받는 사람 집 주소, 아파트명, 또는 랜드마크 (예: '압구정 현대아파트', '강남역', '서울 강남구 역삼동')",
                    },
                    "store_query": {
                        "type": "string",
                        "description": "찾을 매장 종류 (예: '꽃집', '케이크', '베이커리')",
                        "default": "꽃집",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "매장 개수 (기본 3)",
                        "default": 3,
                    },
                    "radius_m": {
                        "type": "integer",
                        "description": "집 주소 기준 검색 반경 (미터, 기본 2000)",
                        "default": 2000,
                    },
                },
                "required": ["address"],
            },
        },
    ]
