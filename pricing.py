"""pricing.py - subtotal, discount and shipping rules."""

from helpers import add_up


def calculate_order_subtotal(order, products):
    """price x quantity for every item, then add them all up.
    (Call this only for a VALID order - validate_order() checks the ids.)"""
    line_totals = [
        products[item["product_id"]]["price"] * item["quantity"]
        for item in order["items"]
    ]
    return add_up(*line_totals)


def get_discount_rate(subtotal):
    """Highest matching slab wins (checked from the biggest to the smallest)."""
    if subtotal >= 1000:
        return 0.15
    if subtotal >= 500:
        return 0.10
    if subtotal >= 200:
        return 0.05
    return 0.0


def calculate_discount(subtotal):
    """Discount amount in dollars."""
    return round(subtotal * get_discount_rate(subtotal), 2)


def calculate_shipping(subtotal):
    """Free shipping from $500 (on the subtotal), otherwise $20."""
    return 0 if subtotal >= 500 else 20
