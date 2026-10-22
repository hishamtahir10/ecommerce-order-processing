"""tests.py - built-in tests (asserts) for normal and edge cases.
Run with:  python main.py --test   (or  python tests.py)"""

from data import get_starter_products, get_starter_orders
from helpers import add_up
from pricing import calculate_order_subtotal, calculate_discount, calculate_shipping
from validation import validate_order
from orders import process_order, process_all_orders
from reports import (generate_sales_report, generate_customer_report,
                     get_low_stock_products)


def run_tests():
    # --- discount slabs (boundaries) ---
    assert calculate_discount(1000) == 150
    assert calculate_discount(1500) == 225
    assert calculate_discount(999.99) == 100.0      # 10% slab
    assert calculate_discount(500) == 50
    assert calculate_discount(499.99) == 25.0       # 5% slab
    assert calculate_discount(200) == 10
    assert calculate_discount(199.99) == 0
    assert calculate_discount(0) == 0

    # --- shipping ---
    assert calculate_shipping(500) == 0
    assert calculate_shipping(499.99) == 20
    assert calculate_shipping(50) == 20

    # --- *args helper ---
    assert add_up() == 0
    assert add_up(10, 20.5, 3) == 33.5

    # --- subtotal ---
    products = get_starter_products()
    first_order = get_starter_orders()[0]
    assert calculate_order_subtotal(first_order, products) == 1250

    # --- validation: required edge cases ---
    def order_with(items, status="paid"):
        return {"order_id": "T", "customer": "Test", "items": items, "payment_status": status}

    ok, _ = validate_order(first_order, products)
    assert ok is True
    ok, why = validate_order(order_with([{"product_id": "P999", "quantity": 1}]), products)
    assert not ok and "Unknown product" in why                       # unknown product
    ok, why = validate_order(order_with([{"product_id": "P001", "quantity": 0}]), products)
    assert not ok and "positive" in why                              # zero quantity
    ok, why = validate_order(order_with([{"product_id": "P001", "quantity": -3}]), products)
    assert not ok and "positive" in why                              # negative quantity
    ok, why = validate_order(order_with([{"product_id": "P001", "quantity": 11}]), products)
    assert not ok and "stock" in why                                 # more than stock
    ok, why = validate_order(order_with([]), products)
    assert not ok and "no items" in why                              # no items
    ok, why = validate_order(order_with([{"product_id": "P001", "quantity": 1}], "refunded"), products)
    assert not ok and "payment status" in why                        # invalid payment status
    ok, why = validate_order(order_with([{"product_id": "P001", "quantity": 1}]), {})
    assert not ok and "Unknown product" in why                       # empty products dict
    ok, _ = validate_order(order_with([{"product_id": "P001", "quantity": 1.5}]), products)
    assert not ok                                                    # non-integer quantity
    ok, _ = validate_order("not an order", products)
    assert not ok                                                    # garbage input
    ok, _ = validate_order(order_with([{"product_id": "P001", "quantity": 6},
                                       {"product_id": "P001", "quantity": 6}]), products)
    assert not ok                                                    # duplicate lines exceed stock

    # --- full run with the starter data ---
    products = get_starter_products()
    processed = process_all_orders(get_starter_orders(), products)
    statuses = [r["status"] for r in processed]
    assert statuses == ["paid", "paid", "pending"]

    assert processed[0]["subtotal"] == 1250 and processed[0]["discount"] == 187.5
    assert processed[0]["shipping"] == 0 and processed[0]["total"] == 1062.5
    assert processed[1]["subtotal"] == 450 and processed[1]["discount"] == 22.5
    assert processed[1]["shipping"] == 20 and processed[1]["total"] == 447.5

    # inventory: reduced ONLY for paid orders (pending ORD003 did not touch Mouse stock)
    assert products["P001"]["stock"] == 9
    assert products["P002"]["stock"] == 48
    assert products["P003"]["stock"] == 18
    assert products["P004"]["stock"] == 14

    report = generate_sales_report(processed, products)
    assert "Total Orders: 3" in report
    assert "Paid Orders: 2" in report
    assert "Pending Orders: 1" in report
    assert "Rejected Orders: 0" in report
    assert "Total Revenue: $1,510.00" in report
    assert "Total Discount: $210.00" in report
    assert "Total Shipping: $20.00" in report
    assert "Top Customer: Ali" in report                            # multiple orders, same customer
    assert "Keyboard, Mouse (tie, 2 units each)" in report         # tie in top-selling product
    assert "- Laptop (P001): 9 left" in report

    customer_report = generate_customer_report(processed)
    assert customer_report["unique_customers"] == {"Ali", "Ahmed"}
    assert customer_report["spend"] == {"Ali": 1062.5, "Ahmed": 447.5}

    # --- rejected order: no stock change, counted as rejected ---
    products = get_starter_products()
    bad = order_with([{"product_id": "P001", "quantity": 99}])
    result = process_order(bad, products)
    assert result["status"] == "rejected" and products["P001"]["stock"] == 10

    # --- stock is checked against the stock LEFT after earlier orders ---
    products = get_starter_products()
    big1 = {"order_id": "A", "customer": "X", "payment_status": "paid",
            "items": [{"product_id": "P001", "quantity": 6}]}
    big2 = {"order_id": "B", "customer": "Y", "payment_status": "paid",
            "items": [{"product_id": "P001", "quantity": 6}]}
    processed = process_all_orders([big1, big2], products)
    assert [r["status"] for r in processed] == ["paid", "rejected"]
    assert products["P001"]["stock"] == 4

    # --- **kwargs options ---
    products = get_starter_products()
    o = {"order_id": "K", "customer": "Z", "payment_status": "paid",
         "items": [{"product_id": "P004", "quantity": 2}]}                # subtotal 600
    assert process_order(o, get_starter_products())["total"] == 540      # 600 - 10% + free shipping
    assert process_order(o, get_starter_products(), apply_discount=False)["total"] == 600
    small = {"order_id": "S", "customer": "Z", "payment_status": "paid",
             "items": [{"product_id": "P002", "quantity": 1}]}           # subtotal 25
    assert process_order(small, get_starter_products())["total"] == 45   # 25 + 20 shipping
    assert process_order(small, get_starter_products(), include_shipping=False)["total"] == 25
    assert process_order(small, get_starter_products(),
                         include_shipping=False, apply_discount=False)["total"] == 25

    # --- empty orders list ---
    report = generate_sales_report([], get_starter_products())
    assert "Total Orders: 0" in report
    assert "Total Revenue: $0.00" in report
    assert "Top Customer: N/A" in report
    assert "Top Selling Product: N/A" in report

    # --- empty products dictionary ---
    processed = process_all_orders(get_starter_orders(), {})
    assert all(r["status"] == "rejected" for r in processed)
    report = generate_sales_report(processed, {})
    assert "Rejected Orders: 3" in report and "- None" in report

    # --- no low-stock products ---
    rich = {"P1": {"name": "Pen", "price": 1, "category": "Office", "stock": 500}}
    assert get_low_stock_products(rich) == []
    assert "- None" in generate_sales_report([], rich)

    # --- configurable low-stock threshold (closure) ---
    assert len(get_low_stock_products(get_starter_products(), 15)) == 2   # Laptop 10, Monitor 15
    assert len(get_low_stock_products(get_starter_products(), 5)) == 0

    # --- missing fields never crash ---
    result = process_order({}, get_starter_products())
    assert result["status"] == "rejected"

    print("All tests passed!")


if __name__ == "__main__":
    run_tests()
