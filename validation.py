"""validation.py - checks whether an order is valid (never crashes)."""


def validate_order(order, products):
    """Return (True, "") if the order is fine, else (False, "reason").
    It never raises an error - a bad order just gets a reason."""
    if not isinstance(order, dict):
        return False, "Order is not a valid dictionary"

    items = order.get("items")
    if not isinstance(items, list) or len(items) == 0:
        return False, "Order has no items"

    if order.get("payment_status") not in ("paid", "pending"):
        return False, "Invalid payment status: " + str(order.get("payment_status"))

    requested = {}  # product_id -> total quantity asked in this order
    for item in items:
        if not isinstance(item, dict):
            return False, "Item is not a valid dictionary"

        product_id = item.get("product_id")
        quantity = item.get("quantity")

        if not isinstance(product_id, str) or product_id not in products:
            return False, "Unknown product ID: " + str(product_id)

        # bool is a subtype of int in Python, so reject it explicitly
        if isinstance(quantity, bool) or not isinstance(quantity, int):
            return False, f"Quantity for {product_id} must be a whole number"
        if quantity <= 0:
            return False, f"Quantity for {product_id} must be positive (got {quantity})"

        requested[product_id] = requested.get(product_id, 0) + quantity

    # Stock check AFTER adding duplicate lines of the same product together
    for product_id, quantity in requested.items():
        available = products[product_id].get("stock", 0)
        if quantity > available:
            return False, f"Insufficient stock for {product_id} (wanted {quantity}, have {available})"

    return True, ""
