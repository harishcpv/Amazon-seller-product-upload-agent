"""Demo presets and synthetic product photo generator for instant testing."""

from typing import Dict, Any, List
from PIL import Image, ImageDraw, ImageFont
import math


DEMO_PRODUCTS = {
    "triply_kadhai": {
        "name": "Manasvini Fancy Triply Stainless Steel Kadhai (2.5L)",
        "product_type": "Triply Stainless Steel Deep Kadhai with Glass Lid",
        "material": "Stainless Steel (Triply 304 Food Grade)",
        "sku": "MF-SS-KAD-24CM",
        "price": 1899.0,
        "mrp": 2799.0,
        "capacity": "2.5 Litres",
        "dimensions": "28 x 25 x 12 cm",
        "weight": "1.35 kg",
        "hsn": "73239390",
        "guidance": "Highlight triply construction, SAS (Steel-Aluminium-Steel) technology, gas & induction compatibility, and heat-resistant riveted handles."
    },
    "cast_iron_skillet": {
        "name": "Manasvini Fancy Pre-Seasoned Cast Iron Skillet (10-Inch)",
        "product_type": "Heavy Duty Pre-Seasoned Cast Iron Frying Pan",
        "material": "Pre-Seasoned Heavy Cast Iron",
        "sku": "MF-CI-PAN-26CM",
        "price": 1499.0,
        "mrp": 2199.0,
        "capacity": "1.8 Litres",
        "dimensions": "42 x 26 x 5 cm",
        "weight": "2.10 kg",
        "hsn": "73239200",
        "guidance": "Highlight natural 100% vegetable oil seasoning, iron enrichment in food, authentic searing capabilities, and heirloom durability."
    },
    "brass_handi": {
        "name": "Manasvini Fancy Traditional Heavy-Gauge Brass Handi with Kalai (3L)",
        "product_type": "Traditional Handcrafted Brass Biryani Handi with Lid",
        "material": "Traditional Heavy Gauge Brass",
        "sku": "MF-BR-HND-30L",
        "price": 2899.0,
        "mrp": 3999.0,
        "capacity": "3.0 Litres",
        "dimensions": "24 x 24 x 16 cm",
        "weight": "1.85 kg",
        "hsn": "74181021",
        "guidance": "Highlight authentic Indian tin lining (kalai), slow-cooking flavor lock, regal royal dining aesthetic, and handcrafted Ayurvedic benefits."
    }
}


def generate_synthetic_demo_image(slot_id: int, product_key: str = "triply_kadhai") -> Image.Image:
    """Generates a high-resolution raw product photo on a non-white studio backdrop

    to demonstrate background removal, centering, and 2000x2000 pure white standardization.
    """
    width, height = 1200, 1200

    # Color palette based on product type
    if "cast_iron" in product_key:
        body_color = (38, 42, 46)
        rim_color = (65, 70, 75)
        specular = (95, 100, 105)
    elif "brass" in product_key:
        body_color = (212, 175, 55)
        rim_color = (235, 200, 80)
        specular = (255, 235, 140)
    else: # Stainless Steel
        body_color = (185, 195, 205)
        rim_color = (220, 230, 240)
        specular = (250, 252, 255)

    # 1. Create a non-white textured studio background (warm gray / wood tint)
    bg = Image.new("RGB", (width, height), (225, 222, 218))
    draw = ImageDraw.Draw(bg)

    # Add subtle backdrop radial shading & floor shadow
    for r in range(width // 2, 0, -20):
        shade = 225 - int(25 * (1 - r / (width // 2)))
        draw.ellipse([width // 2 - r, height // 2 - r, width // 2 + r, height // 2 + r], outline=(shade, shade - 3, shade - 7), width=10)

    # Ground shadow ellipse
    shadow_box = [250, 720, 950, 860]
    draw.ellipse(shadow_box, fill=(175, 172, 168))

    cx, cy = width // 2, height // 2

    # Draw varying angles based on slot_id
    if slot_id == 1:
        # Main Front Angle: Kadhai body, handles, rim, shine
        # Main Bowl
        draw.chord([300, 380, 900, 780], start=0, end=180, fill=body_color, outline=rim_color, width=6)
        # Rim
        draw.ellipse([300, 360, 900, 420], fill=rim_color, outline=specular, width=4)
        # Interior surface
        draw.ellipse([320, 370, 880, 410], fill=(body_color[0] - 20, body_color[1] - 20, body_color[2] - 20))
        # Left Handle
        draw.arc([200, 370, 320, 430], start=90, end=270, fill=(70, 75, 80), width=14)
        # Right Handle
        draw.arc([880, 370, 1000, 430], start=270, end=90, fill=(70, 75, 80), width=14)
        # Specular metallic streak
        draw.line([450, 410, 520, 720], fill=specular, width=12)

    elif slot_id == 2:
        # Side Profile Angle
        draw.chord([340, 400, 860, 770], start=0, end=180, fill=body_color, outline=rim_color, width=5)
        draw.ellipse([340, 385, 860, 430], fill=rim_color)
        # Side handle zoomed
        draw.rectangle([230, 395, 350, 420], fill=(70, 75, 80))
        draw.ellipse([210, 385, 250, 430], fill=(70, 75, 80))
        draw.line([560, 420, 600, 730], fill=specular, width=10)

    elif slot_id == 3:
        # Top-Down Open Cooking Surface
        draw.ellipse([300, 300, 900, 900], fill=body_color, outline=rim_color, width=8)
        # Inner bottom circle
        draw.ellipse([420, 420, 780, 780], fill=(body_color[0] - 15, body_color[1] - 15, body_color[2] - 15), outline=specular, width=3)
        # Top and bottom handles
        draw.arc([220, 550, 310, 650], start=90, end=270, fill=(70, 75, 80), width=16)
        draw.arc([890, 550, 980, 650], start=270, end=90, fill=(70, 75, 80), width=16)

    elif slot_id == 4:
        # Dimensions & Scale diagram view
        draw.chord([320, 410, 880, 770], start=0, end=180, fill=body_color, outline=rim_color, width=5)
        draw.ellipse([320, 390, 880, 435], fill=rim_color)
        # Dimension arrows
        draw.line([300, 350, 900, 350], fill=(210, 50, 40), width=4)
        draw.polygon([(295, 350), (315, 340), (315, 360)], fill=(210, 50, 40))
        draw.polygon([(905, 350), (885, 340), (885, 360)], fill=(210, 50, 40))
        # Height arrow
        draw.line([930, 400, 930, 760], fill=(210, 50, 40), width=4)

    else:
        # In-Use / Packaging Box presentation
        # Gift Box behind
        draw.rectangle([250, 320, 600, 780], fill=(35, 47, 62), outline=(255, 153, 0), width=4)
        # Miniature logo text on box
        draw.rectangle([280, 360, 570, 410], fill=(255, 153, 0))
        # Product in front
        draw.chord([480, 480, 960, 820], start=0, end=180, fill=body_color, outline=rim_color, width=5)
        draw.ellipse([480, 465, 960, 500], fill=rim_color)

    # Stamp a subtle badge
    draw.text((40, 40), f"Manasvini Fancy Studio - Slot {slot_id}", fill=(120, 120, 120))

    return bg
