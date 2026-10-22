"""orders.py - processes orders: validation, pricing, payment status, inventory update."""

from validation import validate_order
from pricing import calculate_order_subtotal, calculate_discount, calculate_shipping


def process_order(order, products, **options):
    """Process ONE order and return a result record (a dictionary).

    Options (**kwargs):
        include_shipping=True  -> add shipping cost (False = no shipping charged)
        apply_discount=True    -> apply the discount slab (False = no discount)

    status in the result is: "paid", "pending" or "rejected".
    Stock is reduced ONLY when the order is valid AND paid.
    """
    include_shipping = options.get("include_shipping", True)
    apply_discount = options.get("apply_discount", True)

    safe_order = order if isinstance(order, dict) else {}
    record = {
        "order_id": safe_order.get("order_id", "UNKNOWN"),
        "customer": safe_order.get("customer", "Unknown"),
        "status": "rejected",
        "items": [],
        "subtotal": 0,
        "discount": 0,
        "shipping": 0,
        "total": 0,
        "reason": "",
    }

    is_valid, reason = validate_order(order, products)
    if not is_valid:
        record["reason"] = reason
        return record

    subtotal = calculate_order_subtotal(order, products)
    discount = calculate_discount(subtotal) if apply_discount else 0
    shipping = calculate_shipping(subtotal) if include_shipping else 0

    record["items"] = [
        {"product_id": item["product_id"], "quantity": item["quantity"]}
        for item in order["items"]
    ]
    record["subtotal"] = subtotal
    record["discount"] = discount
    record["shipping"] = shipping
    record["total"] = round(subtotal - discount + shipping, 2)
    record["status"] = order["payment_status"]  # "paid" or "pending"

    if record["status"] == "paid":
        for item in order["items"]:
            products[item["product_id"]]["stock"] -= item["quantity"]

    return record


def process_all_orders(orders, products, **options):
    """Process orders one by one (in order) and collect the results.
    A crash in one order must never stop the others."""
    processed = []
    for order in orders:
        try:
            processed.append(process_order(order, products, **options))
        except Exception as error:  # safety net - should not normally happen
            processed.append({
                "order_id": "UNKNOWN", "customer": "Unknown", "status": "rejected",
                "items": [], "subtotal": 0, "discount": 0, "shipping": 0,
                "total": 0, "reason": "Unexpected error: " + str(error),
            })
    return processed
