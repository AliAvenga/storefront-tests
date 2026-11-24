from __future__ import annotations

import re

from behave import given, then, when


def _text(html: str, testid: str) -> list[str]:
    return [re.sub(r"<[^>]+>", "", match).strip()
            for match in re.findall(rf'data-testid="{re.escape(testid)}"[^>]*>(.*?)</', html, re.S)]


# ---- storefront account pages
@given('I sign in as "{email}"')
@when('I sign in as "{email}"')
def sign_in(context, email):
    context.reply = context.shop.form("/account/sign-in", {"email": email})
    assert context.reply.status == 200, context.reply.status


@then('the account shows "{name}"')
def account_name(context, name):
    assert _text(context.shop.page("/account").text, "customer-name") == [name]


@then('the account shows {points:d} points and tier "{tier}"')
def account_points(context, points, tier):
    page = context.shop.page("/account").text
    assert _text(page, "loyalty-points") == [str(points)], _text(page, "loyalty-points")
    assert _text(page, "loyalty-tier") == [tier], _text(page, "loyalty-tier")


@then('the account page says "{message}"')
def account_message(context, message):
    assert _text(context.reply.text, "page-message") == [message], _text(context.reply.text, "page-message")


@then("the order says I earned {points:d} points")
def order_points(context, points):
    assert _text(context.reply.text, "points-earned") == [f"You earned {points} loyalty points."], \
        _text(context.reply.text, "points-earned")


@when('I add "{product_id}" to my wishlist')
def add_to_wishlist(context, product_id):
    context.reply = context.shop.form("/wishlist/items", {"product_id": product_id})
    assert context.reply.status == 200 and context.reply.url.endswith("/account"), context.reply.url


@then('my wishlist shows "{product_id}" as "{availability}"')
def wishlist_item(context, product_id, availability):
    items = _text(context.shop.page("/account").text, "wishlist-item")
    assert f"{product_id} · {availability}" in items, items


# ---- customers service API
@when('I award points for order "{order_ref}" worth {amount} to customer "{customer_id}"')
def award(context, order_ref, amount, customer_id):
    context.reply = context.shop.customers(f"/api/customers/loyalty/{customer_id}/awards", "POST",
                                           {"order_ref": order_ref, "amount": amount})
    assert context.reply.status == 201, context.reply.text
    context.customer_id = customer_id


@then('the customer "{customer_id}" has {points:d} points and tier "{tier}"')
def customer_points(context, customer_id, points, tier):
    balance = context.shop.customers(f"/api/customers/loyalty/{customer_id}").json()
    assert (balance["points"], balance["tier"]) == (points, tier), balance


@then('awarding points for order "{order_ref}" again is refused with "{error}"')
def award_again(context, order_ref, error):
    reply = context.shop.customers(f"/api/customers/loyalty/{context.customer_id}/awards", "POST",
                                   {"order_ref": order_ref, "amount": "10.00"})
    assert reply.status == 409 and reply.json()["error"] == error, (reply.status, reply.text)
