import os
import re
from typing import Optional

import httpx

NAVER_SHOP_URL = "https://openapi.naver.com/v1/search/shop.json"
_TAG_RE = re.compile(r"<[^>]+>")


def _strip_html(text: str) -> str:
    return _TAG_RE.sub("", text)


async def search_gifts(
    query: str,
    *,
    limit: int = 3,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
) -> list[dict]:
    client_id = os.environ.get("NAVER_CLIENT_ID")
    client_secret = os.environ.get("NAVER_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise ValueError(
            "NAVER_CLIENT_ID, NAVER_CLIENT_SECRET 환경변수가 필요합니다."
        )

    params: dict = {
        "query": query,
        "display": min(limit * 3, 30),
        "sort": "sim",
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            NAVER_SHOP_URL,
            params=params,
            headers={
                "X-Naver-Client-Id": client_id,
                "X-Naver-Client-Secret": client_secret,
            },
        )
        response.raise_for_status()
        data = response.json()

    results: list[dict] = []
    for item in data.get("items", []):
        price = int(item.get("lprice", 0))
        if price <= 0:
            continue
        if min_price is not None and price < min_price:
            continue
        if max_price is not None and price > max_price:
            continue

        results.append(
            {
                "title": _strip_html(item.get("title", "")),
                "price": price,
                "link": item.get("link", ""),
                "mall_name": item.get("mallName", ""),
                "image": item.get("image", ""),
            }
        )
        if len(results) >= limit:
            break

    return results
