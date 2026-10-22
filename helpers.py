"""helpers.py - small reusable helper functions."""


def add_up(*values):
    """*args demo: add any number of amounts and round to 2 decimals.
    Example: add_up(10, 20.5, 3) -> 33.5"""
    total = 0
    for value in values:
        total += value
    return round(total, 2)


def money(amount):
    """Format a number as money, e.g. 1062.5 -> '$1,062.50'."""
    return f"${amount:,.2f}"
