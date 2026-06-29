MCP_SERVER_INSTRUCTIONS = """\
선물 찾기 MCP 서버입니다. 사용자가 선물, 생일, 기념일, 당일 전달 등을 언급하면 아래 도구를 활용하세요.

1. quick_gift — 온라인 선물 추천 (네이버 쇼핑 실검색 TOP3, 가격·링크)
2. find_gift_pickup — 근처 픽업 매장 검색 (카카오 로컬, 매장명·주소·전화·카카오맵)

데모 시나리오:
유저: "베프 생일인데 3만원대 감성 선물, 오늘 전달"
→ quick_gift(query="감성 선물", max_price=35000, min_price=25000)
→ find_gift_pickup(query="강남역 꽃집") 또는 픽업 가능한 매장 키워드
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
                "카카오 로컬 키워드 검색으로 근처 선물 픽업 매장을 찾습니다. "
                "매장명, 주소, 전화번호, 카카오맵 링크를 반환합니다. "
                "트리거: 오늘 전달, 당일 픽업, 근처 매장, 픽업"
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "검색 키워드 (예: '강남역 꽃집', '홍대 베이커리')",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "매장 개수 (기본 3)",
                        "default": 3,
                    },
                },
                "required": ["query"],
            },
        },
    ]
