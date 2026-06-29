import os


def _get_env(name: str) -> str | None:
    value = os.environ.get(name)
    if value is None:
        return None
    value = value.strip()
    return value or None


def get_kakao_rest_api_key() -> str | None:
    return _get_env("KAKAO_REST_API_KEY")


def get_naver_credentials() -> tuple[str | None, str | None]:
    return _get_env("NAVER_CLIENT_ID"), _get_env("NAVER_CLIENT_SECRET")


def config_status() -> dict:
    naver_id, naver_secret = get_naver_credentials()
    return {
        "kakao_rest_api_key_set": get_kakao_rest_api_key() is not None,
        "naver_client_id_set": naver_id is not None,
        "naver_client_secret_set": naver_secret is not None,
    }
