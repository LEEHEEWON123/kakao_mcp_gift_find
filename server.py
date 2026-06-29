"""
선물 찾기 PlayMCP 서버

- quick_gift: 네이버 쇼핑 실검색 TOP3 (가격·링크)
- find_gift_pickup: 카카오 로컬 근처 픽업 매장 (카카오맵)
"""
import os
from typing import Annotated, Optional

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import Field

load_dotenv()

_mcp = None
_mcp_app = None
_mcp_transport_type = None

app = FastAPI(title="선물 찾기 MCP 서버")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "gift-find-mcp"}


@app.get("/.well-known/mcp")
async def mcp_metadata():
    from src.mcp_tools_schema import (
        MCP_SERVER_INSTRUCTIONS,
        get_mcp_tools_list,
    )

    return {
        "version": "1.0",
        "protocolVersion": "2025-03-26",
        "serverInfo": {
            "name": "gift-find-mcp",
            "title": "선물 찾기 MCP",
            "version": "1.0.0",
        },
        "description": (
            "온라인 선물 추천(네이버) + 근처 픽업 매장(카카오맵)을 한번에 찾는 MCP 서버"
        ),
        "instructions": MCP_SERVER_INSTRUCTIONS,
        "transports": [{"type": "streamable-http", "endpoint": "/"}],
        "transport": {"type": "streamable-http", "endpoint": "/"},
        "capabilities": {
            "tools": {"listChanged": False},
            "resources": {},
            "prompts": {},
        },
        "tools": get_mcp_tools_list(),
    }


@app.get("/")
async def root():
    return {
        "name": "gift-find-mcp",
        "description": "온라인 선물 추천 + 근처 픽업 매장 검색",
        "version": "1.0.0",
        "tools": ["quick_gift", "find_gift_pickup"],
        "endpoints": {"mcp": "/", "health": "/health"},
    }


def _register_tools(mcp):
    from src.naver_shopping import search_gifts

    @mcp.tool(
        description=(
            "[온라인] 네이버 쇼핑 실검색 TOP3 선물 추천. "
            "가격·링크·쇼핑몰명 반환. "
            "트리거: 선물 추천, 가격대, 온라인 구매, 네이버 쇼핑"
        )
    )
    async def quick_gift(
        query: Annotated[str, Field(description="검색 키워드 (예: '감성 선물', '생일 케이크')")],
        limit: Annotated[int, Field(description="추천 개수", ge=1, le=10)] = 3,
        min_price: Annotated[
            Optional[int], Field(description="최소 가격 (원, 예: 25000)")
        ] = None,
        max_price: Annotated[
            Optional[int], Field(description="최대 가격 (원, 예: 35000)")
        ] = None,
    ) -> dict:
        """네이버 쇼핑에서 선물 상품을 검색해 TOP N을 추천합니다."""
        try:
            gifts = await search_gifts(
                query,
                limit=limit,
                min_price=min_price,
                max_price=max_price,
            )
        except httpx.HTTPStatusError as e:
            return {
                "error": f"네이버 API 오류: {e.response.status_code}",
                "query": query,
            }
        except ValueError as e:
            return {"error": str(e), "query": query}

        price_label = _format_price_range(min_price, max_price)
        return {
            "query": query,
            "price_range": price_label,
            "count": len(gifts),
            "gifts": gifts,
            "message": (
                f"'{query}' {price_label} 검색 결과 {len(gifts)}건"
                if gifts
                else f"'{query}' {price_label} 조건에 맞는 상품이 없습니다."
            ),
        }

    @mcp.tool(
        description=(
            "[픽업] 받는 사람 집 주소 기준 오프라인 픽업 매장 검색. "
            "집에서 거리·매장명·주소·전화·카카오맵 링크 반환. "
            "트리거: 오늘 전달, 당일 픽업, 집 근처 매장, 픽업"
        )
    )
    async def find_gift_pickup(
        address: Annotated[
            str,
            Field(
                description="받는 사람 집 주소 또는 랜드마크 (예: '서울 강남구 역삼동', '강남역')"
            ),
        ],
        store_query: Annotated[
            str, Field(description="찾을 매장 종류 (예: '꽃집', '케이크', '베이커리')")
        ] = "꽃집",
        limit: Annotated[int, Field(description="매장 개수", ge=1, le=10)] = 3,
        radius_m: Annotated[
            int, Field(description="집 주소 기준 검색 반경 (미터)", ge=100, le=20000)
        ] = 2000,
    ) -> dict:
        """받는 사람 주소를 기준으로 픽업 가능한 오프라인 매장을 검색합니다."""
        from src.kakao_local import search_pickup_near_address

        try:
            result = await search_pickup_near_address(
                address,
                store_query,
                limit=limit,
                radius=radius_m,
            )
        except httpx.HTTPStatusError as e:
            return {
                "error": f"카카오 API 오류: {e.response.status_code}",
                "address": address,
                "store_query": store_query,
            }
        except ValueError as e:
            return {"error": str(e), "address": address, "store_query": store_query}

        stores = result["stores"]
        geocoded = result["geocoded_address"]
        return {
            **result,
            "count": len(stores),
            "message": (
                f"'{geocoded}' 기준 {radius_m}m 이내 {store_query} {len(stores)}곳"
                if stores
                else f"'{geocoded}' 근처 {store_query} 매장이 없습니다."
            ),
        }


def _format_price_range(
    min_price: Optional[int], max_price: Optional[int]
) -> str:
    if min_price and max_price:
        return f"{min_price:,}~{max_price:,}원"
    if max_price:
        return f"{max_price:,}원 이하"
    if min_price:
        return f"{min_price:,}원 이상"
    return "가격 제한 없음"


def _get_mcp():
    global _mcp

    if _mcp is not None:
        return _mcp

    from fastmcp import FastMCP
    from src.mcp_tools_schema import MCP_SERVER_INSTRUCTIONS

    _mcp = FastMCP(name="gift-find-mcp", instructions=MCP_SERVER_INSTRUCTIONS)
    _register_tools(_mcp)
    return _mcp


def _init_mcp_app():
    global _mcp_app, _mcp_transport_type, app

    try:
        mcp_instance = _get_mcp()

        if hasattr(mcp_instance, "streamable_http_app"):
            try:
                _mcp_app = mcp_instance.streamable_http_app(path="/")
            except TypeError:
                _mcp_app = mcp_instance.streamable_http_app()
            _mcp_transport_type = "Streamable HTTP"
        elif hasattr(mcp_instance, "http_app"):
            try:
                _mcp_app = mcp_instance.http_app(path="/")
            except TypeError:
                _mcp_app = mcp_instance.http_app()
            _mcp_transport_type = "HTTP"
        else:
            raise AttributeError("FastMCP instance has no supported app method")

        if hasattr(_mcp_app, "lifespan"):
            new_app = FastAPI(title="선물 찾기 MCP 서버", lifespan=_mcp_app.lifespan)
            new_app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
            for route in app.routes:
                new_app.routes.append(route)
            app = new_app

        return True
    except Exception as e:
        print(f"Warning: MCP initialization failed: {e}")
        return False


_init_mcp_app()

if _mcp_app is not None:
    app.mount("/", _mcp_app)

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port)
