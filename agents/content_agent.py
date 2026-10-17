"""Content & Attribute Generation Agent for Amazon AutoList Studio.

Performs Image-First AI Inspection on product photos to automatically generate:
- Amazon A9-optimized titles
- 5 benefit-driven bullet points
- Rich HTML product descriptions
- Backend search terms under 249 bytes
- Extracted material, finish, shape, and HSN codes

Supports both Google Gemini Multimodal Vision AI (when API key is present)
and an intelligent Local Computer Vision Analyzer (inspecting pixels, color spectra, and silhouettes).
"""

import os
import json
import re
from typing import Dict, Any, List, Optional
from PIL import Image
import io
from dotenv import load_dotenv, set_key

from core.config import BRAND_PROFILE, AMAZON_LIMITS, GEMINI_CONFIG
from agents.local_vision_analyzer import LocalVisionAnalyzer

# Load environment
load_dotenv()

IMAGE_FIRST_SYSTEM_PROMPT = """You are an elite Amazon e-commerce catalog architect and A9 SEO taxonomist for the premium brand "Manasvini Fancy".

CRITICAL INSTRUCTION - IMAGE ANALYSIS FIRST:
You are inspecting the provided product photograph(s). Your analysis MUST be driven 100% by what is visually shown in the image pixels.
DO NOT use pre-conceived templates or assumptions.
1. Visually identify the exact product (e.g. Copper Water Bottle, Brass Pooja Diya, Cast Iron Tawa, Chef Knife, Spice Container, Tea Kettle, Cookware Pan, Lunch Box, Coffee Mug, etc.).
2. Visually identify the material (Pure Copper, Traditional Brass, Cast Iron, Stainless Steel, Wood, Glass, Ceramic, etc.).
3. Visually identify the finish (Hammered, Mirror Polish, Matte Brushed, Pre-Seasoned, Antique Patina, etc.).
4. Visually identify the shape, proportions, parts (lid, handle, rivets, spouts, stand, scale).

AMAZON LISTING RULES:
1. Product Title:
   Formula: [Manasvini Fancy] + [Material] + [Product Type] + [Capacity / Dimensions] + [Key Visual Highlights & Compatibility]
   - Must be between 100 and 195 characters (Never exceed 200 characters).
   - Use Title Case. Never use ALL CAPS.
   - Prohibited words: DO NOT use "Best", "Sale", "#1", "Free Shipping".

2. Exactly 5 Benefit-Driven Bullet Points:
   - Start EACH bullet point with a capitalized 2-4 word bracketed benefit, followed by colon:
     Example: [TRIPLY THERMAL CRAFTSMANSHIP]: Built with authentic...
   - Bullet 1: Material, Purity & Food-Grade Durability.
   - Bullet 2: Core Utility, Thermal / Liquid Performance & Ergonomics.
   - Bullet 3: Design Details, Handles, Lid, Seals & Aesthetic Finish.
   - Bullet 4: Cooktop / Daily Use Versatility (Induction, Gas, On-The-Go, Home).
   - Bullet 5: Effortless Cleaning, Maintenance & 1-Year Brand Guarantee.

3. Rich HTML Product Description:
   - 250-400 words with <p>, <b>, <ul>, <li> tags tailored to this exact item.

4. Backend Search Terms:
   - High-volume search terms strictly under 249 bytes (no commas, space-separated, no brand names).

OUTPUT FORMAT:
Return ONLY valid JSON matching this schema (no markdown formatting, no code blocks):
{
  "product_name": "Identified product name",
  "title": "Full Amazon title",
  "bullet_1": "string",
  "bullet_2": "string",
  "bullet_3": "string",
  "bullet_4": "string",
  "bullet_5": "string",
  "description": "string",
  "search_terms": "string",
  "material": "string",
  "color": "string",
  "finish_type": "string",
  "item_shape": "string",
  "capacity": "string",
  "item_weight": "string",
  "dimensions": "string",
  "care_instructions": "string",
  "suggested_hsn": "string"
}
"""


class ContentGenerationAgent:
    """Multimodal Content & Attribute Generation Agent."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.brand = BRAND_PROFILE["brand_name"]

    def generate_listing_content(
        self,
        images: List[Image.Image],
        seller_inputs: Optional[Dict[str, Any]] = None,
        user_guidance: str = ""
    ) -> Dict[str, Any]:
        """Generates Amazon listing attributes strictly by analyzing the uploaded product photo(s)."""
        inputs = seller_inputs or {}
        active_images = [img for img in images if img is not None]

        # 1. Try Gemini Multimodal Vision AI if API key is available
        if self.api_key and self.api_key.strip() and active_images:
            try:
                gemini_result = self._call_gemini_multimodal(active_images, inputs, user_guidance)
                if gemini_result:
                    return gemini_result
            except Exception as e:
                print(f"[ContentAgent] Gemini API invocation error: {e}. Falling back to Local Computer Vision.")

        # 2. Local Computer Vision Analyzer (Inspects actual pixels, colors, and shape without API key)
        if active_images:
            return self._call_local_computer_vision(active_images[0], inputs, user_guidance)

        # 3. Last-resort fallback if no image uploaded
        return self._generate_default_fallback(inputs, user_guidance)

    def _call_gemini_multimodal(
        self,
        images: List[Image.Image],
        seller_inputs: Dict[str, Any],
        user_guidance: str
    ) -> Optional[Dict[str, Any]]:
        """Invokes Google Gemini 2.5 Flash with image bytes for deep visual recognition."""
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key.strip())

            prompt_text = f"""
INSPECT THE ATTACHED PRODUCT PHOTO(S):
- Brand Name: {self.brand}
- Optional Seller Note: {user_guidance or 'Identify this product accurately from the photograph and produce a premium Amazon listing.'}
- Target Marketplace: Amazon.in

Please analyze the photo, determine what the product is, its material, finish, and produce the requested JSON listing payload.
"""

            contents = [IMAGE_FIRST_SYSTEM_PROMPT, prompt_text]

            # Attach images as JPEG parts for multimodal inference
            for img in images[:3]:
                thumb = img.copy()
                thumb.thumbnail((1200, 1200))
                buf = io.BytesIO()
                thumb.save(buf, format="JPEG", quality=90)
                contents.append(
                    types.Part.from_bytes(
                        data=buf.getvalue(),
                        mime_type="image/jpeg"
                    )
                )

            model_id = GEMINI_CONFIG["default_model"]
            response = client.models.generate_content(
                model=model_id,
                contents=contents,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    response_mime_type="application/json"
                )
            )

            raw_text = response.text.strip()
            # Clean possible markdown wrapping
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]

            parsed = json.loads(raw_text.strip())
            return self._validate_and_normalize_payload(parsed)

        except Exception as e:
            print(f"[ContentAgent] Failed during Gemini multimodal call: {e}")
            return None

    def _call_local_computer_vision(
        self,
        primary_image: Image.Image,
        seller_inputs: Dict[str, Any],
        user_guidance: str = ""
    ) -> Dict[str, Any]:
        """Runs local pixel and silhouette inspection when no API key is present."""
        visual_data = LocalVisionAnalyzer.analyze_image(primary_image)

        # If user explicitly specified product_type hint in seller_inputs, blend it
        if seller_inputs.get("product_type") and seller_inputs["product_type"] != "Triply Stainless Steel Deep Kadhai with Lid":
            visual_data["product_type"] = seller_inputs["product_type"]

        listing = LocalVisionAnalyzer.generate_listing_from_visuals(visual_data, self.brand)
        listing["detected_visuals"] = visual_data
        return listing

    def _generate_default_fallback(self, seller_inputs: Dict[str, Any], user_guidance: str) -> Dict[str, Any]:
        """Basic fallback when neither images nor API key are available."""
        prod = seller_inputs.get("product_type", "Premium Kitchen Cookware")
        mat = seller_inputs.get("material", "Stainless Steel")
        title = f"{self.brand} {mat} {prod} - Heavy Duty Induction Compatible Premium Cookware"
        return {
            "title": title[:195],
            "bullet_1": f"[PREMIUM FOOD-GRADE CRAFTSMANSHIP]: Built with authentic {mat} engineered for lifetime durability.",
            "bullet_2": "[UNIFORM THERMAL DISTRIBUTION]: Heavy encapsulated thermal base eliminates hotspots for fast cooking.",
            "bullet_3": "[ERGONOMIC SAFE HANDLES]: Sturdy cast handles double-riveted with surgical-grade precision.",
            "bullet_4": "[ALL STOVETOP COMPATIBLE]: Works seamlessly on all heat sources including induction cooktops and gas stoves.",
            "bullet_5": f"[EASY TO CLEAN & DISHWASHER SAFE]: Smooth mirror-finish surface. Backed by {self.brand} 1-Year Guarantee.",
            "description": f"<p>Upgrade your kitchen with {self.brand} {prod}. Engineered from certified {mat} for daily cooking excellence.</p>",
            "search_terms": f"{self.brand.lower()} {mat.lower()} {prod.lower()} kitchen dining cookware utensils",
            "material": mat,
            "color": "Silver Mirror Polish",
            "finish_type": "Mirror Finish",
            "capacity": "Standard Size",
            "item_weight": "1.2 kg",
            "dimensions": "25 x 25 x 10 cm",
            "suggested_hsn": "73239390",
            "source": "Standard Preset Generator"
        }

    def _validate_and_normalize_payload(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validates and enforces Amazon character limits and formatting on LLM outputs."""
        title = data.get("title", "")
        if not title.startswith(self.brand):
            title = f"{self.brand} {title}"
        if len(title) > 200:
            title = title[:197] + "..."

        bullets = [
            data.get("bullet_1", ""),
            data.get("bullet_2", ""),
            data.get("bullet_3", ""),
            data.get("bullet_4", ""),
            data.get("bullet_5", ""),
        ]

        normalized_bullets = []
        for i, b in enumerate(bullets):
            text = b.strip()
            if not text.startswith("["):
                prefixes = [
                    "[PREMIUM CRAFTSMANSHIP]: ",
                    "[SUPERIOR THERMAL PERFORMANCE]: ",
                    "[ERGONOMIC SAFE DESIGN]: ",
                    "[ALL COOKTOP COMPATIBILITY]: ",
                    "[EASY CLEANING & MAINTENANCE]: "
                ]
                text = prefixes[i] + text
            normalized_bullets.append(text[:500])

        search_terms = data.get("search_terms", "")
        clean_terms = re.sub(r"[,\.\-\:\;]", " ", search_terms)
        clean_terms = " ".join(clean_terms.split())[:245]

        return {
            "product_name": data.get("product_name", ""),
            "title": title,
            "bullet_1": normalized_bullets[0],
            "bullet_2": normalized_bullets[1],
            "bullet_3": normalized_bullets[2],
            "bullet_4": normalized_bullets[3],
            "bullet_5": normalized_bullets[4],
            "description": data.get("description", ""),
            "search_terms": clean_terms,
            "material": data.get("material", "Stainless Steel"),
            "color": data.get("color", "Silver Mirror Finish"),
            "finish_type": data.get("finish_type", "Mirror Finish"),
            "item_shape": data.get("item_shape", "Round"),
            "capacity": data.get("capacity", "Standard Size"),
            "item_weight": data.get("item_weight", "1.2 kg"),
            "dimensions": data.get("dimensions", "25 x 25 x 10 cm"),
            "care_instructions": data.get("care_instructions", "Dishwasher Safe"),
            "suggested_hsn": data.get("suggested_hsn", "73239390"),
            "source": "Google Gemini 2.5 Flash Multimodal Vision AI"
        }
