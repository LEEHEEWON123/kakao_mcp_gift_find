import os

import httpx

KAKAO_KEYWORD_URL = "https://dapi.kakao.com/v2/local/search/keyword.json"


async def search_pickup_stores(
    query: str,
    *,
    limit: int = 3,
) -> list[dict]:
    api_key = os.environ.get("KAKAO_REST_API_KEY")
    if not api_key:
        raise ValueError("KAKAO_REST_API_KEY 환경변수가 필요합니다.")

    params: dict = {
        "query": query,
        "size": min(limit, 15),
        "sort": "accuracy",
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            KAKAO_KEYWORD_URL,
            params=params,
            headers={"Authorization": f"KakaoAK {api_key}"},
        )
        response.raise_for_status()
        data = response.json()

    results: list[dict] = []
    for doc in data.get("documents", []):
        address = doc.get("road_address_name") or doc.get("address_name", "")
        distance = doc.get("distance")
        results.append(
            {
                "name": doc.get("place_name", ""),
                "address": address,
                "phone": doc.get("phone", "") or "전화번호 없음",
                "map_url": doc.get("place_url", ""),
                "distance_m": int(distance) if distance else None,
                "category": doc.get("category_name", ""),
            }
        )

    return results[:limit]
