"""Data models and schemas for Amazon AutoList Studio."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


class ProductIdentity(BaseModel):
    """Amazon Seller Central - Product Identity Tab Schema"""
    item_name: str = Field(
        ...,
        description="Product Title optimized for Amazon A9 Search (Max 200 characters)",
        min_length=10,
        max_length=200
    )
    brand_name: str = Field(
        default="Manasvini Fancy",
        description="Brand Name registered on Amazon Brand Registry"
    )
    product_id: str = Field(
        default="GTIN_EXEMPTION_APPLIED",
        description="UPC, EAN, GCID, or GTIN Exemption Status"
    )
    product_id_type: str = Field(
        default="GTIN Exemption",
        description="Product ID Type (GTIN Exemption, UPC, EAN, ASIN)"
    )
    item_type_keyword: str = Field(
        default="cookware-kadhais-and-pans",
        description="Amazon Browse Node / Item Type Keyword"
    )
    model_name: str = Field(
        default="MF-LUXE-TRI",
        description="Model Name"
    )
    model_number: str = Field(
        default="MF-2026-01",
        description="Manufacturer Model Number"
    )

    @field_validator("item_name")
    def validate_title_length(cls, v: str) -> str:
        if len(v.strip()) > 200:
            raise ValueError("Amazon product title cannot exceed 200 characters.")
        return v.strip()


class ProductDescription(BaseModel):
    """Amazon Seller Central - Description Tab Schema"""
    bullet_point_1: str = Field(
        default="",
        description="Bullet Point 1: Premium Material & Build Quality",
        max_length=500
    )
    bullet_point_2: str = Field(
        default="",
        description="Bullet Point 2: Thermal Performance & Cooking Efficiency",
        max_length=500
    )
    bullet_point_3: str = Field(
        default="",
        description="Bullet Point 3: Ergonomic Safety, Handles & Lid Design",
        max_length=500
    )
    bullet_point_4: str = Field(
        default="",
        description="Bullet Point 4: All-Stovetop & Induction Compatibility",
        max_length=500
    )
    bullet_point_5: str = Field(
        default="",
        description="Bullet Point 5: Easy Maintenance & Care Guidance",
        max_length=500
    )
    product_description: str = Field(
        default="",
        description="Rich HTML/formatted product story and details",
        max_length=2000
    )
    search_terms: str = Field(
        default="",
        description="Backend Generic Keywords (Max 249 bytes, space separated, no punctuation)",
        max_length=350
    )

    def get_bullet_points(self) -> List[str]:
        return [
            self.bullet_point_1,
            self.bullet_point_2,
            self.bullet_point_3,
            self.bullet_point_4,
            self.bullet_point_5
        ]


class ProductDetails(BaseModel):
    """Amazon Seller Central - Product Details Tab Schema"""
    material: str = Field(default="Stainless Steel (Triply 304 Food Grade)")
    color: str = Field(default="Silver Mirror Finish")
    finish_type: str = Field(default="Mirror Polished Interior & Brushed Exterior")
    item_shape: str = Field(default="Round Deep Kadhai")
    theme: str = Field(default="Kitchen & Dining")
    target_audience: str = Field(default="Home Cooks, Families, Professional Chefs")
    care_instructions: str = Field(default="Dishwasher Safe, Hand wash with mild liquid soap")
    capacity: str = Field(default="2.5 Litres")
    item_weight: str = Field(default="1.35 kg")
    package_dimensions: str = Field(default="28 x 25 x 12 cm")
    package_length_cm: float = Field(default=28.0)
    package_width_cm: float = Field(default=25.0)
    package_height_cm: float = Field(default=12.0)
    package_weight_kg: float = Field(default=1.5)
    number_of_pieces: int = Field(default=2) # e.g. Kadhai + Stainless Steel Lid
    is_dishwasher_safe: bool = Field(default=True)
    is_induction_compatible: bool = Field(default=True)
    is_oven_safe: bool = Field(default=True)


class OfferPricing(BaseModel):
    """Amazon Seller Central - Offer & Pricing Tab Schema"""
    seller_sku: str = Field(
        default="MF-SS-KAD-24CM",
        description="Unique Seller Stock Keeping Unit identifier"
    )
    standard_price: float = Field(
        default=1899.0,
        description="Selling Price / Your Price (INR)"
    )
    list_price: float = Field(
        default=2799.0,
        description="Maximum Retail Price / MRP (INR)"
    )
    quantity: int = Field(
        default=50,
        description="Available inventory stock quantity"
    )
    fulfillment_channel: str = Field(
        default="DEFAULT",
        description="Merchant Fulfilled (DEFAULT) or Amazon Fulfilled (AMAZON_NA)"
    )
    handling_time: int = Field(
        default=2,
        description="Order lead time to ship in days"
    )
    condition_type: str = Field(
        default="New",
        description="Item Condition"
    )

    @property
    def discount_percent(self) -> float:
        if self.list_price > 0 and self.list_price >= self.standard_price:
            return round(((self.list_price - self.standard_price) / self.list_price) * 100, 1)
        return 0.0


class SafetyCompliance(BaseModel):
    """Amazon Seller Central - Safety & Compliance Tab Schema"""
    country_of_origin: str = Field(default="India")
    hsn_code: str = Field(default="73239390")
    gst_tax_code: str = Field(default="A_GEN_STANDARD")
    manufacturer: str = Field(default="Manasvini Fancy Kitchenware Pvt Ltd")
    packer_details: str = Field(
        default="Manasvini Fancy Logistics Hub, Plot 45/A, Ambattur Industrial Estate, Chennai, Tamil Nadu - 600058"
    )
    importer_details: str = Field(
        default="Manufactured & Marketed in India by Manasvini Fancy Kitchenware Pvt Ltd"
    )
    is_dangerous_goods: bool = Field(default=False)
    batteries_required: bool = Field(default=False)
    warranty_description: str = Field(
        default="1 Year Domestic Manufacturer Warranty against peeling or handle breakage"
    )
    compliance_certification: str = Field(
        default="BIS Compliant, Food Grade SS304 Certified, Lead & Cadmium Free"
    )


class CompleteListing(BaseModel):
    """Unified Amazon Listing Schema bundling all 5 tabs and assets"""
    identity: ProductIdentity
    description: ProductDescription
    details: ProductDetails
    offer: OfferPricing
    compliance: SafetyCompliance
    images_metadata: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: str = Field(default="")
    status: str = Field(default="DRAFT") # DRAFT, READY_TO_EXPORT, SUBMITTED

    def get_summary_dict(self) -> Dict[str, Any]:
        return {
            "SKU": self.offer.seller_sku,
            "Brand": self.identity.brand_name,
            "Title": self.identity.item_name,
            "Price": f"₹{self.offer.standard_price:,.2f}",
            "MRP": f"₹{self.offer.list_price:,.2f}",
            "Discount": f"{self.offer.discount_percent}% OFF",
            "Inventory": self.offer.quantity,
            "HSN Code": self.compliance.hsn_code,
            "Country of Origin": self.compliance.country_of_origin,
            "Fulfillment": "FBA (Fulfilled by Amazon)" if self.offer.fulfillment_channel == "AMAZON_NA" else "Merchant Fulfilled (MFN)",
            "Material": self.details.material,
            "Dimensions": self.details.package_dimensions,
        }
