"""
Mock product catalog — 50 consumer electronics products across 12 categories.
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
    {
        "product_id": "prod-019",
        "name": "Belkin BoostCharge 3-in-1 Wireless Charging Stand",
        "description": (
            "Fast wireless charger designed for iPhone (15W MagSafe), Apple Watch, "
            "and AirPods. Premium weighted chrome finish, landscape and portrait stand mode."
        ),
        "price_inr": 4499.0,
        "stock_quantity": 15,
        "category": "chargers",
    },
    {
        "product_id": "prod-020",
        "name": "Apple 20W USB-C Power Adapter",
        "description": (
            "Official Apple 20W USB-C Power Adapter for rapid charging at home or on the go. "
            "Recommended for pairing with iPhone 15, iPad Pro, and Apple Watch fast charge."
        ),
        "price_inr": 1900.0,
        "stock_quantity": 30,
        "category": "chargers",
    },
    # ── Additional High-Speed Cables ──────────────────────────────────────
    {
        "product_id": "prod-021",
        "name": "Apple Thunderbolt 4 Pro Cable (1.8m)",
        "description": (
            "High-end braided black cable supporting Thunderbolt 4 data transfer up to 40Gbps, "
            "DisplayPort video output (HBR3), and Power Delivery up to 100W."
        ),
        "price_inr": 12900.0,
        "stock_quantity": 5,
        "category": "cables",
    },
    {
        "product_id": "prod-022",
        "name": "UGREEN 8K HDMI 2.1 Ultra High Speed Cable (2m)",
        "description": (
            "Certified HDMI 2.1 cable supporting 8K@60Hz, 4K@120Hz, 48Gbps bandwidth, "
            "eARC, HDR10+, and Dolby Vision for gaming consoles and 4K TV displays."
        ),
        "price_inr": 899.0,
        "stock_quantity": 45,
        "category": "cables",
    },
    {
        "product_id": "prod-023",
        "name": "Baseus 100W 4-in-1 Fast Charging Cable",
        "description": (
            "Versatile multi-connector cable featuring Dual Type-C, Lightning, and Micro USB. "
            "Braided aluminum shell, supports simultaneous multi-device powering up to 100W."
        ),
        "price_inr": 649.0,
        "stock_quantity": 35,
        "category": "cables",
    },
    # ── Magnetic & High-Capacity Power Banks ──────────────────────────────
    {
        "product_id": "prod-024",
        "name": "Anker 622 Magnetic Wireless Battery (MagGo 5000mAh)",
        "description": (
            "Snap-on magnetic wireless portable charger with foldable kickstand for iPhone 15/14/13/12. "
            "Slim 0.5-inch profile with USB-C bi-directional charging."
        ),
        "price_inr": 3499.0,
        "stock_quantity": 18,
        "category": "power_banks",
    },
    {
        "product_id": "prod-025",
        "name": "Anker 737 Power Bank (PowerCore 24K) 140W",
        "description": (
            "Elite 24000mAh 3-port portable charger with smart digital display and 140W ultra-fast output. "
            "Capable of fast charging a 16-inch MacBook Pro or power-hungry gaming laptop."
        ),
        "price_inr": 11999.0,
        "stock_quantity": 6,
        "category": "power_banks",
    },
    # ── Flagship & Budget Earbuds ──────────────────────────────────────────
    {
        "product_id": "prod-026",
        "name": "Apple AirPods Pro (2nd Gen) with MagSafe Case (USB-C)",
        "description": (
            "Flagship in-ear AirPods Pro with pro-level Active Noise Cancellation, Adaptive Audio, "
            "Transparency mode, Personalized Spatial Audio, and precision finding."
        ),
        "price_inr": 22900.0,
        "stock_quantity": 10,
        "category": "earbuds",
    },
    {
        "product_id": "prod-027",
        "name": "Realme Buds Air 5 Pro with Spatial Audio & LDAC",
        "description": (
            "Dual-driver flagship true wireless earbuds with 50dB active noise cancellation, "
            "Hi-Res certified LDAC codec, and 40-hour battery life with fast charge."
        ),
        "price_inr": 4499.0,
        "stock_quantity": 20,
        "category": "earbuds",
    },
    {
        "product_id": "prod-028",
        "name": "Noise Buds VS102 Truly Wireless Earbuds",
        "description": (
            "Ultra-affordable true wireless earbuds featuring 11mm speaker drivers, 50 hours playtime, "
            "Instacharge (10 min charge gives 120 mins), and dedicated gaming mode."
        ),
        "price_inr": 899.0,
        "stock_quantity": 50,
        "category": "earbuds",
    },
    # ── Over-Ear Headphones ───────────────────────────────────────────────
    {
        "product_id": "prod-029",
        "name": "Sony WH-1000XM5 Wireless Noise Cancelling Headphones",
        "description": (
            "Industry-leading noise cancelling over-ear headphones with 8 microphones, Auto NC Optimizer, "
            "30-hour battery, crystal-clear hands-free calling, and ultra-comfortable lightweight leather."
        ),
        "price_inr": 29990.0,
        "stock_quantity": 8,
        "category": "headphones",
    },
    {
        "product_id": "prod-030",
        "name": "Sony WH-CH520 Wireless On-Ear Bluetooth Headphones",
        "description": (
            "Lightweight on-ear wireless headphones with up to 50 hours battery life, DSEE sound enhancement, "
            "multipoint Bluetooth connection, and built-in mic for work calls."
        ),
        "price_inr": 3990.0,
        "stock_quantity": 25,
        "category": "headphones",
    },
    {
        "product_id": "prod-031",
        "name": "JBL Tune 770NC Wireless Adaptive Noise Cancelling Headphones",
        "description": (
            "Over-ear wireless headphones with Adaptive Noise Cancelling, Smart Ambient, 70-hour battery, "
            "JBL Pure Bass Sound, and speed charge (5 min gives 3 hours)."
        ),
        "price_inr": 4999.0,
        "stock_quantity": 18,
        "category": "headphones",
    },
    {
        "product_id": "prod-032",
        "name": "Audio-Technica ATH-M20x Professional Studio Monitor Headphones",
        "description": (
            "Critically acclaimed professional studio monitor headphones with 40mm rare earth neodymium drivers, "
            "tuned for enhanced low-frequency performance and sound isolation."
        ),
        "price_inr": 3850.0,
        "stock_quantity": 14,
        "category": "headphones",
    },
    # ── Portable & Smart Bluetooth Speakers ───────────────────────────────
    {
        "product_id": "prod-033",
        "name": "JBL Flip 6 Portable Waterproof Bluetooth Speaker",
        "description": (
            "Iconic portable Bluetooth speaker with powerful 2-way speaker system, racetrack-shaped woofer, "
            "IP67 waterproof and dustproof, 12 hours playtime, and PartyBoost pairing."
        ),
        "price_inr": 9999.0,
        "stock_quantity": 12,
        "category": "speakers",
    },
    {
        "product_id": "prod-034",
        "name": "boAt Stone 350 10W Portable Bluetooth Speaker",
        "description": (
            "Compact cylindrical 10W stereo speaker with punchy bass, 12 hours playback, IPX7 water resistance, "
            "TWS mode for pairing two speakers, and multiple connectivity modes."
        ),
        "price_inr": 1299.0,
        "stock_quantity": 30,
        "category": "speakers",
    },
    {
        "product_id": "prod-035",
        "name": "Marshall Emberton II Portable Bluetooth Speaker",
        "description": (
            "Custom-tuned Marshall sound with True Stereophonic 360-degree audio, 30+ hours of portable playtime, "
            "IP67 dust and water resistance, and iconic vintage road-tough design."
        ),
        "price_inr": 14999.0,
        "stock_quantity": 7,
        "category": "speakers",
    },
    {
        "product_id": "prod-036",
        "name": "Amazon Echo Dot (5th Gen) Smart Speaker with Alexa",
        "description": (
            "Best sounding Echo Dot yet with clearer vocals, deeper bass and vibrant sound in any room. "
            "Voice control your smart home devices, stream music, and ask questions."
        ),
        "price_inr": 3999.0,
        "stock_quantity": 25,
        "category": "speakers",
    },
    # ── Smartwatches & Fitness Trackers ───────────────────────────────────
    {
        "product_id": "prod-037",
        "name": "Apple Watch Series 9 GPS 41mm Aluminum",
        "description": (
            "Cutting-edge smartwatch powered by the S9 SiP chip, Double Tap gesture control, "
            "brighter 2000-nit display, advanced health sensors including ECG and blood oxygen."
        ),
        "price_inr": 38900.0,
        "stock_quantity": 5,
        "category": "smartwatches",
    },
    {
        "product_id": "prod-038",
        "name": "Noise ColorFit Pro 5 Smartwatch with AMOLED Display",
        "description": (
            "1.85-inch AMOLED display smartwatch with Bluetooth calling, SOS feature, comprehensive "
            "Noise Health Suite (SpO2, heart rate, sleep), and 7-day battery life."
        ),
        "price_inr": 3499.0,
        "stock_quantity": 28,
        "category": "smartwatches",
    },
    {
        "product_id": "prod-039",
        "name": "Amazfit Bip 5 Smartwatch with 1.91-inch Display & GPS",
        "description": (
            "Ultra-large display smartwatch with 4 satellite positioning systems, Bluetooth phone calls, "
            "120+ sports modes, Amazon Alexa built-in, and 10-day battery life."
        ),
        "price_inr": 4499.0,
        "stock_quantity": 16,
        "category": "smartwatches",
    },
    {
        "product_id": "prod-040",
        "name": "Fire-Boltt Ninja Call Pro Plus Bluetooth Calling Watch",
        "description": (
            "Budget Bluetooth calling smartwatch with 1.83-inch HD display, 100 sports modes, AI voice assistant, "
            "SpO2 and continuous heart rate tracking with 280mAh battery."
        ),
        "price_inr": 1199.0,
        "stock_quantity": 40,
        "category": "smartwatches",
    },
    # ── Mechanical & Wireless Keyboards ───────────────────────────────────
    {
        "product_id": "prod-041",
        "name": "Keychron K2 Wireless Mechanical Keyboard (RGB Hot-Swap)",
        "description": (
            "75% compact wireless mechanical keyboard with Gateron G Pro mechanical switches. "
            "Connects with up to 3 devices via Bluetooth 5.1 or wired USB-C. Mac and Windows compatible."
        ),
        "price_inr": 7499.0,
        "stock_quantity": 9,
        "category": "keyboards",
    },
    {
        "product_id": "prod-042",
        "name": "Logitech K380 Multi-Device Bluetooth Wireless Keyboard",
        "description": (
            "Slim, lightweight minimalist keyboard that connects to laptop, tablet, and phone simultaneously. "
            "Easy-switch keys, comfortable scooped keys, 2-year battery life with 2 AAA batteries included."
        ),
        "price_inr": 2695.0,
        "stock_quantity": 35,
        "category": "keyboards",
    },
    {
        "product_id": "prod-043",
        "name": "Redragon K552 Kumara RGB Tenkeyless Mechanical Keyboard",
        "description": (
            "Sturdy compact 87-key tenkeyless mechanical gaming keyboard with dust-proof custom clicky switches, "
            "vibrant rainbow RGB backlighting, and splash-proof metal alloy construction."
        ),
        "price_inr": 2899.0,
        "stock_quantity": 22,
        "category": "keyboards",
    },
    # ── Ergonomic & Gaming Mice ───────────────────────────────────────────
    {
        "product_id": "prod-044",
        "name": "Logitech MX Master 3S Advanced Wireless Performance Mouse",
        "description": (
            "Flagship ergonomic mouse with Quiet Clicks, 8K DPI track-on-glass sensor, "
            "MagSpeed electromagnetic scroll wheel, and ergonomic thumb rest with gestures."
        ),
        "price_inr": 8995.0,
        "stock_quantity": 15,
        "category": "mice",
    },
    {
        "product_id": "prod-045",
        "name": "Logitech M650 L Wireless Mouse for Large Hands",
        "description": (
            "Ergonomic wireless office mouse with SmartWheel precision scrolling, SilentTouch technology, "
            "customizable side buttons, contoured rubber grips, and 24-month battery life."
        ),
        "price_inr": 2995.0,
        "stock_quantity": 30,
        "category": "mice",
    },
    {
        "product_id": "prod-046",
        "name": "Razer DeathAdder Essential Ergonomic Gaming Mouse",
        "description": (
            "Battle-proven gaming mouse with 6,400 DPI optical sensor, classic ergonomic form factor, "
            "5 Hyperesponse buttons rated for 10 million clicks, and green LED lighting."
        ),
        "price_inr": 1399.0,
        "stock_quantity": 40,
        "category": "mice",
    },
    {
        "product_id": "prod-047",
        "name": "ErgoSpire Ergonomic Memory Foam Mouse Pad with Wrist Rest",
        "description": (
            "Comfortable memory foam wrist rest mouse pad that prevents carpal tunnel strain. "
            "Smooth Lycra surface for precise mouse tracking with anti-slip rubberized base."
        ),
        "price_inr": 499.0,
        "stock_quantity": 80,
        "category": "mice",
    },
    # ── High-Speed Portable Storage ───────────────────────────────────────
    {
        "product_id": "prod-048",
        "name": "Samsung T7 Shield 1TB Portable Rugged NVMe SSD",
        "description": (
            "Rugged external solid state drive with transfer speeds up to 1050MB/s (USB 3.2 Gen 2). "
            "IP65 water and dust resistant, 3-meter drop resistant elastomer outer shell."
        ),
        "price_inr": 9499.0,
        "stock_quantity": 14,
        "category": "storage",
    },
    {
        "product_id": "prod-049",
        "name": "SanDisk Ultra Dual Drive Luxe 128GB All-Metal Type-C Flash Drive",
        "description": (
            "2-in-1 all-metal swivel flash drive with reversible USB Type-C and traditional Type-A connectors. "
            "High-speed USB 3.2 Gen 1 performance with up to 400MB/s read speeds."
        ),
        "price_inr": 1199.0,
        "stock_quantity": 50,
        "category": "storage",
    },
    {
        "product_id": "prod-050",
        "name": "Kingston Canvas Select Plus 256GB MicroSD Card with SD Adapter",
        "description": (
            "High-speed Class 10 UHS-I microSD card rated up to 100MB/s. Optimized for Android devices, "
            "action cams, and drones. Rated A1 app performance and Full HD/4K video recording."
        ),
        "price_inr": 1899.0,
        "stock_quantity": 40,
        "category": "storage",
    },
]