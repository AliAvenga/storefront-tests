from __future__ import annotations

import re
from html import unescape

from behave import given, then, when


def _testid(html: str, name: str) -> list[str]:
    """Text of every element with data-testid="name" (one level deep is enough for this demo)."""
    pattern = rf'data-testid="{re.escape(name)}"[^>]*>(.*?)</'
    return [unescape(re.sub(r"<[^>]+>", "", match)).strip() for match in re.findall(pattern, html, re.S)]


# ---- storefront pages
@when("I open the products page")
def open_products(context):
    context.reply = context.shop.page("/products")
    assert context.reply.status == 200, context.reply.status


@then("I see {count:d} products")
def count_products(context, count):
    found = re.findall(r'data-testid="product-card-[^"]+"', context.reply.text)
    assert len(found) == count, f"Expected {count} products, found {len(found)}"


@then('the product "{product_id}" costs "{price}"')
def product_price(context, product_id, price):
    card = re.search(rf'data-testid="product-card-{re.escape(product_id)}".*?</div>', context.reply.text, re.S)
    assert card and f"€{price}" in card.group(0), card.group(0) if card else f"No card for {product_id}"


@when('I open the product page of "{product_id}"')
def open_product(context, product_id):
    context.reply = context.shop.page(f"/products/{product_id}")
    assert context.reply.status == 200, context.reply.status


@then('the stock badge says "{text}"')
def stock_badge(context, text):
    assert _testid(context.reply.text, "stock-badge") == [text], _testid(context.reply.text, "stock-badge")


@then("there is no add to cart button")
def no_add_button(context):
    assert 'data-testid="add-to-cart"' not in context.reply.text


@given('I add {quantity:d} of "{product_id}" to the cart')
@when('I add {quantity:d} of "{product_id}" to the cart')
def add_to_cart(context, quantity, product_id):
    context.reply = context.shop.form("/cart/items", {"product_id": product_id, "quantity": quantity})
    assert context.reply.status == 200 and context.reply.url.endswith("/cart"), (context.reply.status, context.reply.url)


@then('the cart holds {quantity:d} of "{product_id}"')
def cart_holds(context, quantity, product_id):
    page = context.shop.page("/cart").text
    line = re.search(rf"<td>{re.escape(product_id)}</td><td[^>]*>(\d+)</td>", page)
    assert line and int(line.group(1)) == quantity, line.group(0) if line else "Product not in the cart"


@when("I check out")
def check_out(context):
    context.reply = context.shop.form("/checkout", {})


@then("the order is confirmed")
def order_confirmed(context):
    assert "/orders/" in context.reply.url, context.reply.url
    status = re.search(r'data-testid="order-status">(.*?)</p>', context.reply.text, re.S)
    assert status and re.sub(r"<[^>]+>", "", status.group(1)).endswith("is confirmed."), context.reply.text[-400:]


@then('the cart says "{message}"')
def cart_message(context, message):
    assert context.reply.url.split("?")[0].endswith("/cart"), context.reply.url
    assert _testid(context.reply.text, "page-message") == [message], _testid(context.reply.text, "page-message")


# ---- inventory service API
@then('the inventory stock of "{product_id}" is {stock:d}')
def inventory_stock(context, product_id, stock):
    reply = context.shop.inventory(f"/api/inventory/stock/{product_id}")
    assert reply.status == 200 and reply.json()["stock"] == stock, reply.text


@given('I reserve {quantity:d} of "{product_id}" for order "{order_ref}"')
@when('I reserve {quantity:d} of "{product_id}" for order "{order_ref}"')
def reserve(context, quantity, product_id, order_ref):
    context.reply = context.shop.inventory("/api/inventory/reservations", "POST",
                                           {"product_id": product_id, "quantity": quantity, "order_ref": order_ref})
    context.reservation = context.reply.json() if context.reply.status == 201 else None


@then("the reservation is created")
def reservation_created(context):
    assert context.reply.status == 201 and context.reservation["status"] == "reserved", context.reply.text


@then('a low stock event was published for "{product_id}"')
def low_stock_event(context, product_id):
    events = context.shop.inventory("/api/inventory/events?topic=inventory.stock.low").json()["events"]
    assert any(event["payload"]["product_id"] == product_id for event in events), events


@when("I release that reservation")
def release(context):
    context.reply = context.shop.inventory(f"/api/inventory/reservations/{context.reservation['id']}", "DELETE")
    assert context.reply.status == 200 and context.reply.json()["status"] == "released", context.reply.text


@then('the reservation is refused with "{error}"')
def reservation_refused(context, error):
    assert context.reply.status == 409 and context.reply.json()["error"] == error, (context.reply.status,
                                                                                     context.reply.text)
