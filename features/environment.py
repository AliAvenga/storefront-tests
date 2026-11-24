"""Behave hooks for the demo shop. No browser: the tests talk HTTP to the storefront and its services.

Orqestra passes BASE_URL (the app's test or prod URL) and each project's service URL (INVENTORY_SERVICE_URL,
CUSTOMERS_SERVICE_URL); they default to the local ports of demo-application/run.sh.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from support.http import ShopClient  # noqa: E402

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8101").rstrip("/")
INVENTORY_SERVICE_URL = os.environ.get("INVENTORY_SERVICE_URL", "http://localhost:8102").rstrip("/")
CUSTOMERS_SERVICE_URL = os.environ.get("CUSTOMERS_SERVICE_URL", "http://localhost:8103").rstrip("/")


def before_scenario(context, scenario):
    context.shop = ShopClient(BASE_URL, INVENTORY_SERVICE_URL, CUSTOMERS_SERVICE_URL)
    assert context.shop.is_up(), (
        f"The demo shop is not reachable at {BASE_URL}, {INVENTORY_SERVICE_URL} and {CUSTOMERS_SERVICE_URL}. "
        "Start it with demo-application/run.sh."
    )
    context.shop.reset()
