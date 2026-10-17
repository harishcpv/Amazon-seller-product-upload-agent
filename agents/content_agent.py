"""Content & Attribute Generation Agent for Amazon AutoList Studio.

Uses multimodal LLMs (Google Gemini API via google-genai) to analyze product photos
and generate Amazon A9-optimized titles, 5 benefit-driven bullet points, rich descriptions,
and backend search terms tailored for the 'Manasvini Fancy' brand profile.
"""

import os
import json
import re
from typing import Dict, Any, List, Optional
from PIL import Image
import io

from core.config import BRAND_PROFILE, AMAZON_LIMITS, GEMINI_CONFIG
from core.models import ProductIdentity, ProductDescription, ProductDetails, SafetyCompliance


SYSTEM_PROMPT = """You are an elite Amazon e-commerce catalog specialist and A9 SEO optimization architect for the premium kitchenware brand "Manasvini Fancy".
Your mission is to examine the provided product photo(s) and seller inputs, then generate a high-converting, policy-compliant Amazon product listing payload in strict JSON format.

AMAZON COMPLIANCE & A9 BEST PRACTICES:
1. Title Formula:
   [Brand Name: Manasvini Fancy] + [Material/Core Spec: e.g. Triply Stainless Steel / Heavy Pre-Seasoned Cast Iron] + [Product Type: e.g. Deep Kadhai / Frying Pan / Tawa] + [Key Differentiator / Capacity / Lid: e.g. with Stainless Steel Lid, 2.5 Litres, 24cm] + [Compatibility / Use: e.g. Induction & Gas Stove Friendly, Stay-Cool Handles]
   - Title MUST be between 120 and 195 characters (Never exceed 200 characters).
   - Capitalize first letter of every word (Title Case), do NOT use ALL CAPS.
   - Prohibited words: DO NOT use "Best", "Sale", "Top Rated", "Free Shipping", "#1", or emojis.

2. Five Benefit-Driven Bullet Points:
   - Exactly 5 bullet points.
   - Format: Start EACH bullet point with a capitalized 2-4 word benefit in square brackets, followed by a colon and 2-3 detailed sentences.
     Example: [TRIPLY FOOD-GRADE CRAFTSMANSHIP]: Engineered with SS304 inner food-safe layer, aluminum core for uniform heat transfer, and magnetic SS430 outer base.
   - Bullet 1: Material, Construction & Food-Grade Durability.
   - Bullet 2: Heat Distribution, Energy Efficiency & Thermal Retention.
   - Bullet 3: Ergonomic Design, Stay-Cool Riveted Handles & Precision Lid.
   - Bullet 4: Universal Stovetop & Cooktop Compatibility (Induction, Gas, Electric, Halogen).
   - Bullet 5: Effortless Cleaning, Stain Resistance & Care Guidance.
   - Each bullet point MUST be between 150 and 350 characters.

3. Rich Product Description:
   - 250-400 words structured with clean HTML tags (<p>, <b>, <ul>, <li>).
   - Tell the story of "Manasvini Fancy" heritage, cooking experience, durability, and health advantages.

4. Backend Search Terms (Generic Keywords):
   - High-intent search terms under 249 bytes (Amazon strict limit).
   - Lowercase, separated ONLY by single space. No punctuation, no commas, no brand names, no duplicate words.

5. Extracted Product Details:
   - Identify: material, color, finish_type, item_shape, capacity, item_weight, care_instructions.

OUTPUT FORMAT:
Return ONLY valid raw JSON with this exact schema (no markdown fences, no explanatory text):
{
  "title": "string",
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
  "care_instructions": "string",
  "suggested_hsn": "73239390"
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
        seller_inputs: Dict[str, Any],
        user_guidance: str = ""
    ) -> Dict[str, Any]:
        """Generates Amazon listing attributes via Gemini API or intelligent fallback engine."""
        # Try Gemini API if key is present
        if self.api_key and self.api_key.strip():
            try:
                gemini_result = self._call_gemini_multimodal(images, seller_inputs, user_guidance)
                if gemini_result:
                    return gemini_result
            except Exception as e:
                print(f"[ContentAgent] Gemini API invocation error: {e}. Falling back to Smart Rule Engine.")

        # Fallback to deterministic AI Rule Engine
        return self._generate_intelligent_fallback(seller_inputs, user_guidance)

    def _call_gemini_multimodal(
        self,
        images: List[Image.Image],
        seller_inputs: Dict[str, Any],
        user_guidance: str
    ) -> Optional[Dict[str, Any]]:
        """Invokes the Google GenAI SDK (google-genai) with image parts and prompt."""
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key.strip())

            # Prepare contents: prompt + images
            prompt_context = f"""
SELLER PROVIDED VARIABLES:
- Product Type / Keyword: {seller_inputs.get('product_type', 'Kitchen Cookware')}
- Material Preference: {seller_inputs.get('material', 'Stainless Steel')}
- SKU: {seller_inputs.get('sku', 'MF-SS-COOK-01')}
- Selling Price: ₹{seller_inputs.get('price', 1899)} (MRP: ₹{seller_inputs.get('mrp', 2799)})
- Package Dimensions: {seller_inputs.get('dimensions', '28 x 25 x 12 cm')}
- Weight: {seller_inputs.get('weight', '1.35 kg')}
- Capacity: {seller_inputs.get('capacity', '2.5 Litres')}
- Custom Seller Guidance: {user_guidance or 'Focus on authentic Indian cooking, durability, and premium finish.'}
- Target Brand: {self.brand}
"""

            contents = [SYSTEM_PROMPT, prompt_context]

            # Add up to 3 key images for multimodal inspection
            for i, img in enumerate(images[:3]):
                if img is not None:
                    # Resize thumbnail for fast multimodal transmission
                    thumb = img.copy()
                    thumb.thumbnail((1024, 1024))
                    buf = io.BytesIO()
                    thumb.save(buf, format="JPEG", quality=85)
                    img_bytes = buf.getvalue()
                    contents.append(
                        types.Part.from_bytes(
                            data=img_bytes,
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
            return self._validate_and_normalize_payload(parsed, seller_inputs)

        except Exception as e:
            print(f"[ContentAgent] Failed during Gemini multimodal call: {e}")
            return None

    def _generate_intelligent_fallback(
        self,
        seller_inputs: Dict[str, Any],
        user_guidance: str = ""
    ) -> Dict[str, Any]:
        """High-converting, deterministic Amazon listing synthesis engine for Manasvini Fancy products."""
        prod_type = seller_inputs.get("product_type", "Triply Stainless Steel Deep Kadhai with Lid").strip()
        material = seller_inputs.get("material", "Stainless Steel (Triply 304 Food Grade)").strip()
        capacity = seller_inputs.get("capacity", "2.5 Litres").strip()
        sku = seller_inputs.get("sku", "MF-SS-KAD-24CM").strip()
        weight = seller_inputs.get("weight", "1.35 kg").strip()
        dim = seller_inputs.get("dimensions", "28 x 25 x 12 cm").strip()

        # Build Title according to Amazon A9 Formula
        # Brand + Material + Type + Specs + Usability
        title = f"{self.brand} {material} {prod_type} ({capacity}, {dim}) - Induction & Gas Compatible Heavy Gauge Cookware with Stay-Cool Handles"
        if len(title) > 198:
            title = title[:195] + "..."

        # Generate 5 Benefit-Driven Bullet Points
        bullet_1 = f"[PREMIUM FOOD-GRADE CRAFTSMANSHIP]: Built with authentic {material} engineered for lifetime durability. Features a non-reactive inner cooking surface that preserves authentic flavors without leaching toxins or metallic tastes."
        bullet_2 = f"[SUPERIOR TRIPLE-LAYER HEAT RETENTION]: Heavy encapsulated thermal base distributes heat evenly across the entire surface, eliminating hotspots and cooking your dishes up to 20% faster while saving fuel."
        bullet_3 = f"[ERGONOMIC STAY-COOL RIVETED HANDLES]: Sturdy cast handles double-riveted with surgical-grade precision for an ultra-secure, comfortable grip even when bearing heavy gravies and curries."
        bullet_4 = f"[ALL COOKTOP & INDUCTION FRIENDLY]: Seamlessly engineered for all heat sources including induction cooktops, gas stoves, ceramic, halogen, and oven-safe up to 260°C (500°F)."
        bullet_5 = f"[EASY TO CLEAN & DISHWASHER SAFE]: Smooth mirror-finish surface resists stubborn burnt food residues and stains. Rinses effortlessly with mild soap or in the dishwasher for hassle-free maintenance."

        # Generate Rich HTML Description
        description = f"""<p><b>Elevate Your Culinary Experience with {self.brand}</b></p>
<p>At <b>{self.brand}</b>, we believe that true kitchen mastery begins with exceptional cookware. The {self.brand} {prod_type} combines timeless Indian culinary tradition with state-of-the-art multi-layer thermal engineering. Whether you are searing spices, simmering rich curries, deep frying snacks, or preparing everyday family meals, this {prod_type.lower()} delivers unmatched consistency and thermal precision.</p>

<p><b>Engineered for Health and Durability</b><br>
Crafted from certified {material}, our cookware provides 100% toxin-free cooking with zero chemical coatings. The heavy base ensures uniform heat transfer, preventing scorching and preserving essential nutrients and rich aromas.</p>

<p><b>Key Highlights:</b></p>
<ul>
  <li><b>Capacity:</b> {capacity} | <b>Dimensions:</b> {dim} | <b>Weight:</b> {weight}</li>
  <li><b>Cooktop Versatility:</b> 100% Induction & Gas Stove Compatible</li>
  <li><b>Handle Ergonomics:</b> Heat-resistant, heavy-duty double-riveted handles</li>
  <li><b>Maintenance:</b> Dishwasher safe; easy hand-wash with gentle sponge</li>
  <li><b>Backed by Manasvini Fancy Guarantee:</b> 1-Year Manufacturer Warranty</li>
</ul>
<p>Transform everyday cooking into a joyful culinary art. Add the <b>{self.brand} {prod_type}</b> to your kitchen today!</p>"""

        # Generate Backend Search Terms (< 249 bytes)
        raw_terms = f"stainless steel kadai triply deep fry pan induction bottom cooking utensils indian kitchenware {prod_type.lower()} heavy gauge cookware skillet pot with lid"
        # Ensure under 249 bytes
        search_terms = raw_terms[:245]

        # Determine HSN code
        hsn = "73239390"
        if "cast iron" in material.lower():
            hsn = "73239200"
        elif "brass" in material.lower() or "copper" in material.lower():
            hsn = "74181021"

        return {
            "title": title,
            "bullet_1": bullet_1,
            "bullet_2": bullet_2,
            "bullet_3": bullet_3,
            "bullet_4": bullet_4,
            "bullet_5": bullet_5,
            "description": description,
            "search_terms": search_terms,
            "material": material,
            "color": "Silver Mirror Polish",
            "finish_type": "Mirror Polished Inner, Brushed Outer",
            "item_shape": "Round Deep Kadhai",
            "capacity": capacity,
            "item_weight": weight,
            "care_instructions": "Dishwasher Safe. Avoid harsh steel wool scrubbers.",
            "suggested_hsn": hsn,
            "source": "Smart Heuristic Rule Engine (Production Presets)"
        }

    def _validate_and_normalize_payload(self, data: Dict[str, Any], seller_inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Validates and enforces Amazon character limits and formatting on LLM outputs."""
        title = data.get("title", "")
        # Ensure Brand name is at start of title
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

        # Ensure bullet points have bracketed header
        normalized_bullets = []
        for i, b in enumerate(bullets):
            text = b.strip()
            if not text.startswith("["):
                prefixes = [
                    "[PREMIUM CRAFTSMANSHIP]: ",
                    "[UNIFORM HEAT DISTRIBUTION]: ",
                    "[ERGONOMIC SAFE HANDLES]: ",
                    "[ALL STOVETOP COMPATIBLE]: ",
                    "[EASY CLEANING & CARE]: "
                ]
                text = prefixes[i] + text
            normalized_bullets.append(text[:500])

        search_terms = data.get("search_terms", "")
        # Strip punctuation and commas
        clean_terms = re.sub(r"[,\.\-\:\;]", " ", search_terms)
        clean_terms = " ".join(clean_terms.split())[:245]

        return {
            "title": title,
            "bullet_1": normalized_bullets[0],
            "bullet_2": normalized_bullets[1],
            "bullet_3": normalized_bullets[2],
            "bullet_4": normalized_bullets[3],
            "bullet_5": normalized_bullets[4],
            "description": data.get("description", ""),
            "search_terms": clean_terms,
            "material": data.get("material", seller_inputs.get("material", "Stainless Steel")),
            "color": data.get("color", "Silver Mirror Finish"),
            "finish_type": data.get("finish_type", "Mirror Finish"),
            "item_shape": data.get("item_shape", "Round"),
            "capacity": data.get("capacity", seller_inputs.get("capacity", "2.5 Litres")),
            "item_weight": data.get("item_weight", seller_inputs.get("weight", "1.35 kg")),
            "care_instructions": data.get("care_instructions", "Dishwasher Safe"),
            "suggested_hsn": data.get("suggested_hsn", "73239390"),
            "source": "Google Gemini Multimodal AI"
        }
