from typing import Optional

import httpx

from src.config import get_kakao_rest_api_key

KAKAO_KEYWORD_URL = "https://dapi.kakao.com/v2/local/search/keyword.json"
KAKAO_ADDRESS_URL = "https://dapi.kakao.com/v2/local/search/address.json"


def _get_api_key() -> str:
    api_key = get_kakao_rest_api_key()
    if not api_key:
        raise ValueError(
            "KAKAO_REST_API_KEY 환경변수가 필요합니다. "
            "Render 대시보드 Environment에 키를 등록한 뒤 재배포하세요."
        )
    return api_key


def _auth_headers(api_key: str) -> dict[str, str]:
    return {"Authorization": f"KakaoAK {api_key}"}


def _format_distance(meters: Optional[int]) -> Optional[str]:
    if meters is None:
        return None
    if meters < 1000:
        return f"{meters}m"
    return f"{meters / 1000:.1f}km"


async def geocode_address(address: str) -> dict:
    api_key = _get_api_key()

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            KAKAO_ADDRESS_URL,
            params={"query": address},
            headers=_auth_headers(api_key),
        )
        response.raise_for_status()
        data = response.json()

    documents = data.get("documents", [])
    if not documents:
        raise ValueError(f"주소를 찾을 수 없습니다: {address}")

    doc = documents[0]
    road = doc.get("road_address")
    jibun = doc.get("address")

    resolved = ""
    if road:
        resolved = road.get("address_name", "")
    elif jibun:
        resolved = jibun.get("address_name", "")

    return {
        "input": address,
        "resolved_address": resolved or address,
        "longitude": float(doc["x"]),
        "latitude": float(doc["y"]),
    }


def _parse_store(doc: dict) -> dict:
    address = doc.get("road_address_name") or doc.get("address_name", "")
    distance = doc.get("distance")
    distance_m = int(distance) if distance else None

    return {
        "name": doc.get("place_name", ""),
        "address": address,
        "phone": doc.get("phone", "") or "전화번호 없음",
        "map_url": doc.get("place_url", ""),
        "distance_m": distance_m,
        "distance_label": _format_distance(distance_m),
        "latitude": float(doc["y"]) if doc.get("y") else None,
        "longitude": float(doc["x"]) if doc.get("x") else None,
        "category": doc.get("category_name", ""),
    }


async def search_pickup_near_address(
    address: str,
    store_query: str,
    *,
    limit: int = 3,
    radius: int = 2000,
) -> dict:
    anchor = await geocode_address(address)
    api_key = _get_api_key()

    params = {
        "query": store_query,
        "x": str(anchor["longitude"]),
        "y": str(anchor["latitude"]),
        "radius": min(max(radius, 0), 20000),
        "sort": "distance",
        "size": min(limit, 15),
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            KAKAO_KEYWORD_URL,
            params=params,
            headers=_auth_headers(api_key),
        )
        response.raise_for_status()
        data = response.json()

    stores = [_parse_store(doc) for doc in data.get("documents", [])][:limit]

    return {
        "recipient_address": address,
        "geocoded_address": anchor["resolved_address"],
        "anchor": {
            "latitude": anchor["latitude"],
            "longitude": anchor["longitude"],
        },
        "store_query": store_query,
        "radius_m": radius,
        "stores": stores,
    }


async def search_pickup_stores(
    query: str,
    *,
    limit: int = 3,
) -> list[dict]:
    """키워드만으로 검색 (하위 호환). address+store_query 사용을 권장."""
    api_key = _get_api_key()

    params = {
        "query": query,
        "size": min(limit, 15),
        "sort": "accuracy",
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            KAKAO_KEYWORD_URL,
            params=params,
            headers=_auth_headers(api_key),
        )
        response.raise_for_status()
        data = response.json()

    return [_parse_store(doc) for doc in data.get("documents", [])][:limit]
