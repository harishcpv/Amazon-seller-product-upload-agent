"""Application configuration and brand presets for Amazon AutoList Studio."""

import os
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables from .env if available
load_dotenv()

# App Info
APP_NAME = "Amazon AutoList Studio"
APP_TAGLINE = "AI-Powered Amazon Listing Automation Engine"
APP_VERSION = "1.0.0"

# Brand Store Profile: "Manasvini Fancy"
BRAND_PROFILE = {
    "brand_name": os.getenv("DEFAULT_BRAND_NAME", "Manasvini Fancy"),
    "legal_entity": "Manasvini Fancy Kitchenware Pvt Ltd",
    "store_tagline": "Crafted Elegance for Modern Indian Kitchens",
    "manufacturer": os.getenv("DEFAULT_MANUFACTURER", "Manasvini Fancy Kitchenware Pvt Ltd"),
    "packer_details": "Manasvini Fancy Logistics Hub, Plot 45/A, Ambattur Industrial Estate, Chennai, Tamil Nadu - 600058, India",
    "importer_details": "Manufactured & Marketed in India by Manasvini Fancy Kitchenware Pvt Ltd",
    "country_of_origin": os.getenv("DEFAULT_COUNTRY_OF_ORIGIN", "India"),
    "country_code": "IN",
    "currency": "INR",
    "currency_symbol": "₹",
    "default_warranty": "1 Year Domestic Warranty against Manufacturing Defects",
    "default_handling_time": 2, # Days
    "default_condition": "New",
    "default_tax_code": "A_GEN_STANDARD", # Standard GST
    "marketplace_id": "A21TJRUUN4KGV", # Amazon India Marketplace ID
    "marketplace_name": "Amazon.in",
}

# Standard HSN Code Directory for Kitchenware & Home Products
HSN_CODES: Dict[str, Dict[str, Any]] = {
    "73239390": {
        "category": "Stainless Steel Kitchenware / Tableware",
        "description": "Table, kitchen or other household articles of stainless steel (Kadhais, Pans, Pots, Cookware)",
        "gst_rate": 18,
        "default_material": "Stainless Steel",
    },
    "73239200": {
        "category": "Cast Iron Cookware",
        "description": "Cast iron skillets, tawas, dutch ovens, and pans",
        "gst_rate": 18,
        "default_material": "Cast Iron",
    },
    "74181021": {
        "category": "Brass & Copper Utensils",
        "description": "Table, kitchen or household articles of copper/brass, traditional serveware",
        "gst_rate": 18,
        "default_material": "Brass / Copper",
    },
    "76151011": {
        "category": "Aluminium Non-Stick Cookware",
        "description": "Pressure cookers, non-stick frying pans, cookware sets",
        "gst_rate": 18,
        "default_material": "Aluminium",
    },
    "82159900": {
        "category": "Cutlery & Kitchen Tools",
        "description": "Spoons, ladles, skimmers, tongs, and kitchen utensils",
        "gst_rate": 18,
        "default_material": "Stainless Steel",
    },
    "70134900": {
        "category": "Glass Containers & Serveware",
        "description": "Glass storage jars, bowls, and microwave-safe containers",
        "gst_rate": 18,
        "default_material": "Borosilicate Glass",
    },
    "69111011": {
        "category": "Ceramic Tableware",
        "description": "Ceramic dinner plates, mugs, and serving bowls",
        "gst_rate": 18,
        "default_material": "Ceramic",
    },
}

# Image Processing Specifications (Amazon Main & Secondary Image Compliance)
IMAGE_CONFIG = {
    "target_width": 2000,
    "target_height": 2000,
    "target_dimension": (2000, 2000),
    "pure_white_rgb": (255, 255, 255),
    "pure_white_hex": "#FFFFFF",
    "product_fill_ratio": 0.85, # Product fills 85% of frame (Amazon standard)
    "padding_margin": 0.075, # 7.5% margins on top/bottom/sides
    "color_space": "RGB",
    "output_format": "JPEG",
    "output_quality": 95,
    "max_file_size_mb": 10.0,
    "slot_names": [
        "Main Image (Pure White #FFFFFF Background)",
        "Angle 2 - Side Profile & Handle Detail",
        "Angle 3 - Top / Interior Cooking Surface",
        "Angle 4 - Dimensions, Capacity & Scale",
        "Angle 5 - In-Use / Packaging & Box Presentation",
    ],
    "slot_codes": ["MAIN", "PT01", "PT02", "PT03", "PT04"]
}

# Amazon A9 Algorithm Rules & Character Limits
AMAZON_LIMITS = {
    "title_min_chars": 50,
    "title_max_chars": 200,
    "bullet_count": 5,
    "bullet_max_chars": 500,
    "bullet_min_chars": 30,
    "description_max_chars": 2000,
    "description_min_chars": 100,
    "search_terms_max_bytes": 249, # Amazon strict backend keyword limit
}

# Material Options
MATERIAL_PRESETS: List[str] = [
    "Stainless Steel (Triply 304 Food Grade)",
    "Pure Heavy-Duty Stainless Steel",
    "Pre-Seasoned Heavy Cast Iron",
    "Traditional Heavy Gauge Brass",
    "Pure Copper Handcrafted",
    "Hard Anodized Aluminium",
    "Ceramic Non-Stick Coated",
    "Borosilicate Thermal Glass"
]

# Theme & Category Presets
THEME_PRESETS: List[str] = [
    "Kitchen & Dining",
    "Cookware & Bakeware",
    "Tableware & Dinnerware",
    "Pots & Pans",
    "Traditional Indian Utensils",
    "Kitchen Storage & Organization"
]

# Target Audience Presets
AUDIENCE_PRESETS: List[str] = [
    "Home Cooks, Families, Professional Chefs",
    "Modern Homemakers & Kitchen Enthusiasts",
    "Health-Conscious Cooking Enthusiasts",
    "Festive Gifting & Housewarming Buyers",
    "Culinary Professionals & Restaurants"
]

# Gemini API Model Settings
GEMINI_CONFIG = {
    "api_key": os.getenv("GEMINI_API_KEY", ""),
    "default_model": "gemini-2.5-flash",
    "fallback_model": "gemini-1.5-flash",
    "temperature": 0.2, # Low temperature for factual, guideline-compliant outputs
    "max_tokens": 2048,
}
