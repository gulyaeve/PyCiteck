import io
from time import time
from typing import Sequence
import anyio
from httpx import AsyncClient


class CiteckClient:
    def __init__(
        self,
        citeck_base_url: str,
        keycloak_client_id: str,
        keycloak_secret: str,
        keycloak_realm: str = "ecos-app",
        client: AsyncClient | None = None
    ):
        self._client = client or AsyncClient()
        self._keycloak_client_id = keycloak_client_id
        self._keycloak_secret = keycloak_secret
        self._citeck_base_url = citeck_base_url
        self._keycloak_realm = keycloak_realm
    
    @property
    def token_url(self):
        return f"{self._citeck_base_url}/ecos-idp/auth/realms/{self._keycloak_realm}/protocol/openid-connect/token"

    @property
    def records_base_url(self):
        return f"{self._citeck_base_url}/gateway/api/records"

    _token_cache = {
        "access_token": None,
        "expires_at": 0,
    }

    async def _get_bearer_token(self, force=False):
        """
        Получение токена OAuth2 (client_credentials) с учетом expires_in.
        """
        now = int(time())
        if (
            not force
            and self._token_cache["access_token"]
            and self._token_cache["expires_at"] - 15 > now
        ):
            return self._token_cache["access_token"]

        data = {
            "grant_type": "client_credentials",
            "client_id": self._keycloak_client_id,
            "client_secret": self._keycloak_secret,
        }

        resp = await self._client.post(self.token_url, data=data)
        token_data = resp.json()

        token = token_data.get("access_token")
        expires_in = int(token_data.get("expires_in", 300))

        self._token_cache["access_token"] = token
        self._token_cache["expires_at"] = now + expires_in
        return token
 
    async def mutate(self, records: Sequence):
        url = f"{self.records_base_url}/mutate"
        token = await self._get_bearer_token()

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        data = {
            "records": records,
            "version": 1,
        }

        resp = await self._client.post(url, json=data, headers=headers)
        result = resp.json()
        return result
    
    async def query(self, query: dict):
        url = f"{self.records_base_url}/query"
        token = await self._get_bearer_token()

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        resp = await self._client.post(url, json=query, headers=headers)
        result = resp.json()
        return result
    
    async def download_file_from_citeck(self, url: str):
        token = await self._get_bearer_token()
        headers = {"Authorization": f"Bearer {token}"}
        file_buffer = io.BytesIO()

        async with self._client as session:
            async with session.stream("GET", url, headers=headers, follow_redirects=True) as response:
                response.raise_for_status()
                
                async for chunk in response.aiter_bytes():
                    file_buffer.write(chunk)

        file_buffer.seek(0)
        return file_buffer

    async def upload_file_to_citeck(
        self,
        url: str,
        path_to_file: str,
        file_name: str,
        file_content_type: str,
    ):
        token = await self._get_bearer_token
        headers = {"Authorization": f"Bearer {token}"}

        async with await anyio.open_file(path_to_file, "rb") as f:
            file_bytes = await f.read()

        files = {
            "file": (file_name, file_bytes, file_content_type)
        }

        response = await self._client.post(url, headers=headers, files=files)
        return response.json()