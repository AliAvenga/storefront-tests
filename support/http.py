"""A small HTTP client for the demo shop, on the standard library only (cookies kept for the cart)."""
from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from http.cookiejar import CookieJar
from typing import Any


@dataclass
class Reply:
    status: int
    text: str
    url: str

    def json(self) -> Any:
        return json.loads(self.text) if self.text else None


class ShopClient:
    def __init__(self, base_url: str, inventory_url: str, timeout: float = 10) -> None:
        self.base_url, self.inventory_url, self.timeout = base_url, inventory_url, timeout
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))

    def _send(self, url: str, method: str = "GET", data: bytes | None = None,
              headers: dict[str, str] | None = None) -> Reply:
        request = urllib.request.Request(url, data=data, method=method, headers=headers or {})
        try:
            with self.opener.open(request, timeout=self.timeout) as response:
                return Reply(response.status, response.read().decode(), response.geturl())
        except urllib.error.HTTPError as error:
            return Reply(error.code, error.read().decode(), url)

    # storefront pages
    def page(self, path: str) -> Reply:
        return self._send(self.base_url + path)

    def form(self, path: str, fields: dict[str, Any]) -> Reply:
        body = urllib.parse.urlencode(fields).encode()
        return self._send(self.base_url + path, "POST", body, {"Content-Type": "application/x-www-form-urlencoded"})

    # inventory service API
    def inventory(self, path: str, method: str = "GET", body: Any = None) -> Reply:
        data = json.dumps(body).encode() if body is not None else None
        headers = {"Content-Type": "application/json"} if data else {}
        return self._send(self.inventory_url + path, method, data, headers)

    def is_up(self) -> bool:
        try:
            return self.page("/health").status == 200 and self.inventory("/health").status == 200
        except OSError:
            return False

    def reset(self) -> None:
        self._send(self.base_url + "/test/reset", "POST", b"")
        self.inventory("/api/inventory/test/reset", "POST")
