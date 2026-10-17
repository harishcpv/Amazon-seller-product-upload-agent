"""Attribute Pre-filler Agent for Amazon AutoList Studio.

Automatically pre-fills standard Seller Central attributes for the 'Manasvini Fancy'
brand profile, provides intelligent HSN code auto-lookup, and generates SKU conventions.
"""

from typing import Dict, Any, Optional
from core.config import BRAND_PROFILE, HSN_CODES, MATERIAL_PRESETS, THEME_PRESETS, AUDIENCE_PRESETS
from core.models import ProductIdentity, ProductDetails, SafetyCompliance, OfferPricing


class AttributePrefillerAgent:
    """Agent that pre-fills store profile constants, HSN codes, and compliance details."""

    def __init__(self, brand_profile: Optional[Dict[str, Any]] = None):
        self.profile = brand_profile or BRAND_PROFILE

    def get_default_identity(self, initial_title: str = "") -> ProductIdentity:
        """Returns pre-filled Product Identity defaults."""
        return ProductIdentity(
            item_name=initial_title or f"{self.profile['brand_name']} Premium Kitchen Cookware",
            brand_name=self.profile["brand_name"],
            product_id="GTIN_EXEMPTION_APPLIED",
            product_id_type="GTIN Exemption",
            item_type_keyword="cookware-kadhais-and-pans",
            model_name="MF-SIGNATURE-SERIES",
            model_number="MF-2026-V1"
        )

    def get_default_details(self, material_choice: str = "Stainless Steel") -> ProductDetails:
        """Returns pre-filled Product Details for Manasvini Fancy."""
        # Find matching material preset
        selected_material = "Stainless Steel (Triply 304 Food Grade)"
        for mat in MATERIAL_PRESETS:
            if material_choice.lower() in mat.lower():
                selected_material = mat
                break

        return ProductDetails(
            material=selected_material,
            color="Silver Mirror Polish" if "steel" in selected_material.lower() else "Matte Black",
            finish_type="Mirror Polished Interior & Brushed Base",
            item_shape="Deep Round Bottom Kadhai",
            theme=THEME_PRESETS[0], # Kitchen & Dining
            target_audience=AUDIENCE_PRESETS[0],
            care_instructions="Dishwasher Safe. For cast iron, hand wash and season with light cooking oil.",
            capacity="2.5 Litres",
            item_weight="1.35 kg",
            package_dimensions="28 x 25 x 12 cm",
            package_length_cm=28.0,
            package_width_cm=25.0,
            package_height_cm=12.0,
            package_weight_kg=1.5,
            number_of_pieces=2,
            is_dishwasher_safe=True,
            is_induction_compatible=True,
            is_oven_safe=True
        )

    def get_default_offer(
        self,
        sku: str = "",
        price: float = 1899.0,
        mrp: float = 2799.0,
        qty: int = 50
    ) -> OfferPricing:
        """Returns pre-filled Offer & Pricing defaults."""
        generated_sku = sku or self.generate_suggested_sku("SS", "KAD", "24CM")
        return OfferPricing(
            seller_sku=generated_sku,
            standard_price=price,
            list_price=mrp,
            quantity=qty,
            fulfillment_channel="DEFAULT", # Merchant Fulfilled MFN
            handling_time=self.profile["default_handling_time"],
            condition_type=self.profile["default_condition"]
        )

    def get_default_compliance(self, material: str = "Stainless Steel") -> SafetyCompliance:
        """Returns pre-filled Safety & Compliance defaults with auto-detected HSN."""
        hsn = self.lookup_hsn_code(material)
        return SafetyCompliance(
            country_of_origin=self.profile["country_of_origin"],
            hsn_code=hsn,
            gst_tax_code=self.profile["default_tax_code"],
            manufacturer=self.profile["manufacturer"],
            packer_details=self.profile["packer_details"],
            importer_details=self.profile["importer_details"],
            is_dangerous_goods=False,
            batteries_required=False,
            warranty_description=self.profile["default_warranty"],
            compliance_certification="Food Grade Certified, BIS Approved, Heavy Metal Leaching Safe"
        )

    def lookup_hsn_code(self, material_or_category: str) -> str:
        """Intelligently matches material/category string to standard Indian GST HSN codes."""
        text = material_or_category.lower()
        if "cast iron" in text or "iron" in text:
            return "73239200"
        elif "brass" in text or "copper" in text:
            return "74181021"
        elif "aluminium" in text or "aluminum" in text:
            return "76151011"
        elif "cutlery" in text or "spoon" in text or "knife" in text:
            return "82159900"
        elif "glass" in text:
            return "70134900"
        elif "ceramic" in text:
            return "69111011"
        else:
            # Default to Stainless Steel Kitchenware
            return "73239390"

    def generate_suggested_sku(self, material_code: str, product_code: str, spec: str) -> str:
        """Generates clean, standardized Amazon SKU format: MF-[MAT]-[PROD]-[SPEC]."""
        mat = material_code.strip().upper()[:3]
        prod = product_code.strip().upper()[:3]
        sp = spec.strip().upper().replace(" ", "")[:5]
        return f"MF-{mat}-{prod}-{sp}"
