"""
Mock product catalog — 18 consumer electronics products.
"""

PRODUCTS = [
    # ── Fast Chargers ─────────────────────────────────────────────────────
    {
        "product_id": "prod-001",
        "name": "Anker 65W USB-C GaN Fast Charger",
        "description": (
            "Compact GaN fast charger supporting 65W USB-C Power Delivery. "
            "Compatible with laptops, MacBooks, iPhones, and Android phones. "
            "Foldable plug, travel-friendly design with surge protection."
        ),
        "price_inr": 1899.0,
        "stock_quantity": 25,
        "category": "chargers",
    },
    {
        "product_id": "prod-002",
        "name": "Belkin 20W USB-C iPhone Fast Charger",
        "description": (
            "20W USB-C Power Delivery fast charger for iPhone 12, 13, 14, 15 series. "
            "Charges iPhone 50% in 30 minutes. Compact wall adapter with foldable prongs."
        ),
        "price_inr": 999.0,
        "stock_quantity": 40,
        "category": "chargers",
    },
    {
        "product_id": "prod-003",
        "name": "OnePlus 80W SUPERVOOC Warp Charger",
        "description": (
            "Official 80W SUPERVOOC fast charger for OnePlus and OPPO smartphones. "
            "Charges 0 to 100 percent in under 30 minutes. Includes USB-A to USB-C cable."
        ),
        "price_inr": 1299.0,
        "stock_quantity": 18,
        "category": "chargers",
    },
    {
        "product_id": "prod-004",
        "name": "UGREEN 30W Mini Fast Charger",
        "description": (
            "Pocket-sized 30W GaN charger with USB-C port. Supports PD 3.0, PPS, "
            "and Quick Charge 4+. Works with all modern smartphones and earbuds. "
            "Weighs just 47 grams."
        ),
        "price_inr": 699.0,
        "stock_quantity": 50,
        "category": "chargers",
    },
    {
        "product_id": "prod-005",
        "name": "Samsung 45W Super Fast Charger 2.0",
        "description": (
            "45W USB-C super fast charger for Samsung Galaxy S23, S24, Z Fold, Z Flip. "
            "Supports USB PD 3.0 PPS. Charges Galaxy S23 from 0 to 70 percent in 30 minutes."
        ),
        "price_inr": 2199.0,
        "stock_quantity": 0,  # intentionally out of stock for demo
        "category": "chargers",
    },
    # ── USB-C Cables ──────────────────────────────────────────────────────
    {
        "product_id": "prod-006",
        "name": "Anker 240W USB-C to USB-C Braided Cable (2m)",
        "description": (
            "Heavy-duty braided nylon USB-C cable rated at 240W power delivery. "
            "Supports 40Gbps data transfer and 8K video output. 2 metre length. "
            "Compatible with USB4, Thunderbolt 3 and 4."
        ),
        "price_inr": 799.0,
        "stock_quantity": 60,
        "category": "cables",
    },
    {
        "product_id": "prod-007",
        "name": "boAt USB-C to Lightning Cable (1m)",
        "description": (
            "MFi certified USB-C to Lightning cable for Apple iPhones and AirPods. "
            "Supports fast charging up to 20W. Tangle-free flat design, 1 metre length."
        ),
        "price_inr": 349.0,
        "stock_quantity": 75,
        "category": "cables",
    },
    # ── Power Banks ───────────────────────────────────────────────────────
    {
        "product_id": "prod-008",
        "name": "Mi 20000mAh 33W Fast Charge Power Bank",
        "description": (
            "20000mAh high-capacity power bank with 33W fast charging output. "
            "Dual USB-A and one USB-C port. LED power indicator. Can charge "
            "a smartphone 4-5 times. Slim and lightweight design."
        ),
        "price_inr": 1799.0,
        "stock_quantity": 20,
        "category": "power_banks",
    },
    {
        "product_id": "prod-009",
        "name": "Anker PowerCore 10000 PD Compact Power Bank",
        "description": (
            "Ultra-compact 10000mAh power bank with 18W USB-C Power Delivery. "
            "Fits in a pocket. Charges iPhones and Android phones twice. "
            "High-speed recharging via USB-C input."
        ),
        "price_inr": 2499.0,
        "stock_quantity": 15,
        "category": "power_banks",
    },
    {
        "product_id": "prod-010",
        "name": "Ambrane 27000mAh 65W Laptop Power Bank",
        "description": (
            "Large capacity 27000mAh power bank with 65W USB-C PD output for laptops. "
            "Can charge a MacBook Air multiple times. Includes USB-A, USB-C ports and "
            "a built-in LED torch."
        ),
        "price_inr": 2999.0,
        "stock_quantity": 8,
        "category": "power_banks",
    },
    # ── Wireless Earbuds ──────────────────────────────────────────────────
    {
        "product_id": "prod-011",
        "name": "boAt Airdopes 141 Wireless Earbuds",
        "description": (
            "True wireless Bluetooth 5.1 earbuds with 42-hour total playback. "
            "IPX4 water resistance, BEAST mode for gaming, responsive touch controls. "
            "Lightweight half-in-ear design."
        ),
        "price_inr": 999.0,
        "stock_quantity": 35,
        "category": "earbuds",
    },
    {
        "product_id": "prod-012",
        "name": "OnePlus Nord Buds 2 ANC Earbuds",
        "description": (
            "Active noise cancellation TWS earbuds with 36dB noise reduction. "
            "12.4mm dynamic drivers, 25 hours battery life with ANC off. "
            "IP55 rated, low latency gaming mode."
        ),
        "price_inr": 2499.0,
        "stock_quantity": 12,
        "category": "earbuds",
    },
    {
        "product_id": "prod-013",
        "name": "Sony WF-C700N Noise Cancelling Earbuds",
        "description": (
            "Sony premium noise cancelling earbuds with LDAC high-res audio support. "
            "15 hours battery with ANC, IPX4 splash resistant, multipoint connection, "
            "360 Reality Audio support."
        ),
        "price_inr": 5999.0,
        "stock_quantity": 6,
        "category": "earbuds",
    },
    # ── Phone Cases ───────────────────────────────────────────────────────
    {
        "product_id": "prod-014",
        "name": "Spigen Ultra Hybrid iPhone 15 Case",
        "description": (
            "Military-grade drop protection case for iPhone 15 with clear back panel. "
            "Air cushion corners, scratch-resistant coating, shows original phone design. "
            "Precise cutouts for all ports and buttons."
        ),
        "price_inr": 899.0,
        "stock_quantity": 30,
        "category": "cases",
    },
    {
        "product_id": "prod-015",
        "name": "Ringke Fusion Samsung Galaxy S24 Case",
        "description": (
            "Transparent hybrid case for Samsung Galaxy S24 with reinforced bumper. "
            "Dot matrix pattern prevents cloudiness, supports wireless charging. "
            "Shock-absorbing TPU + polycarbonate back."
        ),
        "price_inr": 699.0,
        "stock_quantity": 22,
        "category": "cases",
    },
    # ── Screen Protectors ─────────────────────────────────────────────────
    {
        "product_id": "prod-016",
        "name": "Spigen Tempered Glass Screen Protector (iPhone 15)",
        "description": (
            "9H hardness premium tempered glass screen protector for iPhone 15. "
            "Case-friendly fit, anti-fingerprint oleophobic coating, easy installation "
            "with alignment frame included. Pack of 2."
        ),
        "price_inr": 499.0,
        "stock_quantity": 45,
        "category": "screen_protectors",
    },
    {
        "product_id": "prod-017",
        "name": "ZAGG InvisibleShield Ultra Clear+ Screen Protector",
        "description": (
            "Self-healing screen film with lifetime replacement guarantee. "
            "Absorbs impact without cracking, preserves touchscreen sensitivity. "
            "Available for iPhone 15, Samsung Galaxy S24."
        ),
        "price_inr": 799.0,
        "stock_quantity": 18,
        "category": "screen_protectors",
    },
    # ── Multi-Port Charging Hubs ──────────────────────────────────────────
    {
        "product_id": "prod-018",
        "name": "Anker 100W 4-Port USB-C Desktop Charging Station",
        "description": (
            "Desktop GaN charging hub with 4 ports: 2x USB-C (100W, 20W) + 2x USB-A. "
            "Charge laptop, phone, earbuds and tablet simultaneously. "
            "Intelligent power distribution, foldable plug."
        ),
        "price_inr": 3499.0,
        "stock_quantity": 10,
        "category": "chargers",
    },
]