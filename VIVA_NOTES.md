# Viva Notes – E-Commerce Order Processing (Roman Urdu)

## Files ka kaam
| File | Kaam |
|---|---|
| `main.py` | Program yahan se shuru hota hai. `python main.py` demo chalata hai, `--test` tests |
| `data.py` | Starter products aur orders (functions se fresh copy milti hai, global variable nahi) |
| `helpers.py` | `add_up(*values)` (*args) aur `money()` formatting |
| `pricing.py` | `calculate_order_subtotal`, `calculate_discount`, `calculate_shipping` |
| `validation.py` | `validate_order` – order sahi hai ya nahi, reason ke sath |
| `orders.py` | `process_order(order, products, **options)` aur `process_all_orders` |
| `reports.py` | Customer report, product report, low stock, final sales report |
| `tests.py` | Asserts se saare normal aur edge case tests |

## Program ka flow (1 minute mein)
1. `main.py` -> `process_all_orders` har order ko `process_order` ko deta hai.
2. `process_order` pehle `validate_order` chalata hai. Galat ho to status = "rejected" (reason ke sath), stock nahi badalta.
3. Valid ho to subtotal -> discount -> shipping -> total nikalta hai (`pricing.py`).
4. "paid" ho to stock kam hota hai. "pending" ho to stock nahi ghatta aur revenue mein nahi ginta.
5. `generate_sales_report` (`reports.py`) sab results se report banata hai.

## Mumkin sawal aur jawab

**Q: Code multiple files mein kyun hai?**
Taake har kaam alag ho: data, pricing, validation, processing, reports. Padhna aur test karna aasan hota hai. Files ek dusri ko `import` se use karti hain (jaise `from pricing import calculate_discount`).

**Q: Classes kyun nahi use ki?**
Assessment mein mana tha. Sab kuch functions se kiya hai, data dictionaries aur lists mein hai.

**Q: Rejected, pending aur paid mein kya farq hai?**
Rejected = order invalid (stock kam, galat ID, qty <= 0 waghera). Pending = valid hai lekin payment nahi hui. Paid = valid + payment ho gayi. Sirf paid revenue aur stock par asar dalta hai.

**Q: Discount aur shipping subtotal par kyun lagi?**
Assignment ke mutabiq: discount slab subtotal se chunta hai, shipping bhi subtotal >= 500 par free. Total = subtotal - discount + shipping.

**Q: Revenue mein shipping shamil hai?**
Haan, revenue = customer ne jitna total pay kiya (discount ke baad + shipping). Agar sir shipping alag chahein to `reports.py` ke `generate_sales_report` mein `total_revenue` ki line mein `r["total"]` ki jagah `r["subtotal"] - r["discount"]` kar dein.

**Q: Ek hi product do baar order mein ho to stock check kaise hota hai?**
`validate_order` mein `requested` dictionary same product ki quantities jama karti hai, phir total ko stock se compare karta hai.

**Q: Ek order ne stock khatam kar diya to agla order?**
Orders ek ek karke chalte hain aur paid order ke baad stock update ho jata hai, to agla order bacha hua stock dekhta hai.

**Q: `**kwargs` kahan use hua?**
`orders.py` mein `process_order(order, products, **options)`. `options.get("include_shipping", True)` aur `options.get("apply_discount", True)`.

**Q: `*args` kahan use hua?**
`helpers.py` mein `add_up(*values)`. Kitni bhi values de sakte hain, jaise `add_up(*line_totals)`.

**Q: Lambda kahan use hua?**
`reports.py` mein sorting: `sorted(spend.items(), key=lambda pair: (-pair[1], pair[0]))` (zyada spend pehle, barabar ho to naam alphabetical). Low stock sorting mein bhi.

**Q: Comprehension aur sets kahan hain?**
List comprehension: `line_totals` (`pricing.py`). Set comprehension: `unique_customers` aur `sold_categories` (`reports.py`).

**Q: LEGB kahan dikhaya?**
`reports.py` mein `make_low_stock_checker(threshold)`: andar wala `is_low()` apne bahar wale function ka `threshold` use karta hai (Enclosing scope). Local = function ke andar ke variables. Global = file level functions (koi global variable use nahi kiya). Built-in = `len`, `max`, `sorted` waghera.

**Q: Tie ho to kya hota hai?**
Top product/customer ki list banti hai, sab barabar wale dikhte hain. Starter data mein Mouse aur Keyboard dono 2 units, to "Keyboard, Mouse (tie...)" aata hai.

**Q: Low stock ka matlab?**
Stock <= 10. `generate_sales_report(..., low_stock_threshold=10)` se badal sakte hain. Koi na ho to "- None".

**Q: Program crash kyun nahi hota?**
`validate_order` type, missing keys, galat qty sab check karta hai aur crash ki jagah reason deta hai. `process_all_orders` mein try/except safety net bhi hai.

**Q: Edge cases kahan test hue?**
`tests.py` mein asserts: unknown product, zero/negative qty, qty > stock, no items, invalid payment, empty products, empty orders, same customer ke multiple orders, tie, no low stock. Chalane ke liye `python main.py --test`.

## Starter data ka expected result
- ORD001: subtotal 1250, discount 187.50 (15%), shipping 0, total 1062.50 (paid)
- ORD002: subtotal 450, discount 22.50 (5%), shipping 20, total 447.50 (paid)
- ORD003: pending (revenue mein nahi, stock nahi ghata)
- Revenue $1,510.00, Discount $210.00, Shipping $20.00
- Top customer Ali, top product tie Keyboard/Mouse, low stock: Laptop (9 left)
