"""Amazon Inventory Flat File Generator.

Generates official Amazon Inventory Flat File templates (Tab-delimited .tsv / .txt and .csv)
conforming to Amazon Seller Central Category Listing Template standards.
"""

import io
import csv
from typing import Dict, Any, List
from core.models import CompleteListing


class AmazonFlatFileGenerator:
    """Generates ready-to-upload Amazon Inventory Flat Files."""

    # Official Amazon Seller Central Technical Headers
    COLUMNS = [
        ("feed_product_type", "Product Type"),
        ("item_sku", "Seller SKU"),
        ("brand_name", "Brand Name"),
        ("item_name", "Product Name / Title"),
        ("external_product_id", "Product ID (UPC/EAN/GTIN)"),
        ("external_product_id_type", "Product ID Type"),
        ("item_type", "Item Type Keyword"),
        ("standard_price", "Standard Price"),
        ("list_price", "List Price / MRP"),
        ("currency", "Currency"),
        ("quantity", "Quantity"),
        ("fulfillment_channel", "Fulfillment Channel"),
        ("fulfillment_latency", "Handling Time (Days)"),
        ("condition_type", "Item Condition"),
        ("bullet_point1", "Key Product Features 1"),
        ("bullet_point2", "Key Product Features 2"),
        ("bullet_point3", "Key Product Features 3"),
        ("bullet_point4", "Key Product Features 4"),
        ("bullet_point5", "Key Product Features 5"),
        ("product_description", "Product Description"),
        ("generic_keywords", "Search Terms"),
        ("main_image_url", "Main Image URL / Filename"),
        ("other_image_url1", "Other Image URL 1"),
        ("other_image_url2", "Other Image URL 2"),
        ("other_image_url3", "Other Image URL 3"),
        ("other_image_url4", "Other Image URL 4"),
        ("material_type", "Material Type"),
        ("color_name", "Color"),
        ("finish_type", "Finish Type"),
        ("item_shape", "Shape"),
        ("capacity", "Capacity"),
        ("item_weight", "Item Weight"),
        ("package_length", "Package Length (cm)"),
        ("package_width", "Package Width (cm)"),
        ("package_height", "Package Height (cm)"),
        ("package_weight", "Package Weight (kg)"),
        ("country_of_origin", "Country of Origin"),
        ("hsn_code", "HSN Code"),
        ("product_tax_code", "Product Tax Code"),
        ("manufacturer", "Manufacturer"),
        ("packer_contact_information", "Packer Details"),
        ("importer_contact_information", "Importer Details"),
        ("is_fragile", "Is Fragile"),
        ("batteries_required", "Batteries Required"),
        ("warranty_description", "Warranty Description"),
    ]

    @classmethod
    def generate_row_dict(cls, listing: CompleteListing) -> Dict[str, Any]:
        """Maps CompleteListing schema to flat file columns."""
        ident = listing.identity
        desc = listing.description
        det = listing.details
        off = listing.offer
        comp = listing.compliance

        return {
            "feed_product_type": "cookware",
            "item_sku": off.seller_sku,
            "brand_name": ident.brand_name,
            "item_name": ident.item_name,
            "external_product_id": ident.product_id,
            "external_product_id_type": ident.product_id_type,
            "item_type": ident.item_type_keyword,
            "standard_price": f"{off.standard_price:.2f}",
            "list_price": f"{off.list_price:.2f}",
            "currency": "INR",
            "quantity": off.quantity,
            "fulfillment_channel": off.fulfillment_channel,
            "fulfillment_latency": off.handling_time,
            "condition_type": off.condition_type,
            "bullet_point1": desc.bullet_point_1,
            "bullet_point2": desc.bullet_point_2,
            "bullet_point3": desc.bullet_point_3,
            "bullet_point4": desc.bullet_point_4,
            "bullet_point5": desc.bullet_point_5,
            "product_description": desc.product_description,
            "generic_keywords": desc.search_terms,
            "main_image_url": "MAIN_IMAGE.jpg",
            "other_image_url1": "PT01_ANGLE2.jpg",
            "other_image_url2": "PT02_ANGLE3.jpg",
            "other_image_url3": "PT03_DIMENSIONS.jpg",
            "other_image_url4": "PT04_INUSE.jpg",
            "material_type": det.material,
            "color_name": det.color,
            "finish_type": det.finish_type,
            "item_shape": det.item_shape,
            "capacity": det.capacity,
            "item_weight": det.item_weight,
            "package_length": det.package_length_cm,
            "package_width": det.package_width_cm,
            "package_height": det.package_height_cm,
            "package_weight": det.package_weight_kg,
            "country_of_origin": comp.country_of_origin,
            "hsn_code": comp.hsn_code,
            "product_tax_code": comp.gst_tax_code,
            "manufacturer": comp.manufacturer,
            "packer_contact_information": comp.packer_details,
            "importer_contact_information": comp.importer_details,
            "is_fragile": "false",
            "batteries_required": "false",
            "warranty_description": comp.warranty_description,
        }

    @classmethod
    def generate_tsv(cls, listing: CompleteListing) -> str:
        """Generates Amazon official Tab-Delimited text (.tsv / .txt) format with 3-row headers."""
        output = io.StringIO()
        writer = csv.writer(output, delimiter="\t", lineterminator="\n")

        # Row 1: Amazon Template Metadata / Signature
        writer.writerow(["TemplateType=fptcustom", "Version=2026.04", "Marketplace=Amazon.in"])

        # Row 2: Human readable column names
        writer.writerow([label for _, label in cls.COLUMNS])

        # Row 3: Technical column names
        writer.writerow([tech for tech, _ in cls.COLUMNS])

        # Data Row
        data_dict = cls.generate_row_dict(listing)
        row = [str(data_dict.get(tech, "")) for tech, _ in cls.COLUMNS]
        writer.writerow(row)

        return output.getvalue()

    @classmethod
    def generate_csv(cls, listing: CompleteListing) -> str:
        """Generates standard CSV format with human-readable headers for spreadsheets."""
        output = io.StringIO()
        writer = csv.writer(output, lineterminator="\n")

        # Technical & Readable headers
        writer.writerow([tech for tech, _ in cls.COLUMNS])
        data_dict = cls.generate_row_dict(listing)
        row = [str(data_dict.get(tech, "")) for tech, _ in cls.COLUMNS]
        writer.writerow(row)

        return output.getvalue()
