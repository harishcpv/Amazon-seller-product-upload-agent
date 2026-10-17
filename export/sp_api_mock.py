"""Amazon Selling Partner API (SP-API) Mock and Automated Push Engine.

Constructs official SP-API Listings Items API JSON payloads (2021-08-01 specification)
and Feeds API payloads, with pre-flight policy validation and feed submission simulation.
"""

import time
import uuid
import json
from typing import Dict, Any, List
from core.models import CompleteListing
from core.config import BRAND_PROFILE


class AmazonSPAPIMockEngine:
    """Simulates Amazon Selling Partner API Listings Items & Feeds API interactions."""

    MARKETPLACE_ID = BRAND_PROFILE["marketplace_id"] # Amazon India
    API_VERSION = "2021-08-01"

    @classmethod
    def generate_listings_item_payload(cls, listing: CompleteListing) -> Dict[str, Any]:
        """Constructs authentic Amazon SP-API Listings Item JSON schema.

        Endpoint: PUT /listings/2021-08-01/items/{sellerId}/{sku}?marketplaceIds=A21TJRUUN4KGV
        """
        ident = listing.identity
        desc = listing.description
        det = listing.details
        off = listing.offer
        comp = listing.compliance

        bullets_payload = [
            {"value": b, "language_tag": "en_IN", "marketplace_id": cls.MARKETPLACE_ID}
            for b in desc.get_bullet_points() if b
        ]

        payload = {
            "productType": "COOKWARE",
            "requirements": "LISTING",
            "attributes": {
                "item_name": [
                    {
                        "value": ident.item_name,
                        "language_tag": "en_IN",
                        "marketplace_id": cls.MARKETPLACE_ID
                    }
                ],
                "brand": [
                    {
                        "value": ident.brand_name,
                        "language_tag": "en_IN",
                        "marketplace_id": cls.MARKETPLACE_ID
                    }
                ],
                "bullet_point": bullets_payload,
                "product_description": [
                    {
                        "value": desc.product_description,
                        "language_tag": "en_IN",
                        "marketplace_id": cls.MARKETPLACE_ID
                    }
                ],
                "generic_keyword": [
                    {
                        "value": desc.search_terms,
                        "language_tag": "en_IN",
                        "marketplace_id": cls.MARKETPLACE_ID
                    }
                ],
                "purchasable_offer": [
                    {
                        "currency": "INR",
                        "our_price": [
                            {
                                "schedule": [
                                    {
                                        "value_with_tax": off.standard_price
                                    }
                                ]
                            }
                        ],
                        "marketplace_id": cls.MARKETPLACE_ID
                    }
                ],
                "list_price": [
                    {
                        "value_with_tax": off.list_price,
                        "currency": "INR",
                        "marketplace_id": cls.MARKETPLACE_ID
                    }
                ],
                "fulfillment_availability": [
                    {
                        "fulfillment_channel_code": off.fulfillment_channel,
                        "quantity": off.quantity
                    }
                ],
                "lead_time_to_ship_max_days": [
                    {
                        "value": off.handling_time
                    }
                ],
                "condition_type": [
                    {
                        "value": "new_new"
                    }
                ],
                "material": [
                    {
                        "value": det.material,
                        "language_tag": "en_IN"
                    }
                ],
                "color": [
                    {
                        "value": det.color,
                        "language_tag": "en_IN"
                    }
                ],
                "finish_type": [
                    {
                        "value": det.finish_type,
                        "language_tag": "en_IN"
                    }
                ],
                "capacity": [
                    {
                        "value": det.capacity,
                        "unit": "litres"
                    }
                ],
                "country_of_origin": [
                    {
                        "value": "IN"
                    }
                ],
                "hsn_code": [
                    {
                        "value": comp.hsn_code
                    }
                ],
                "manufacturer": [
                    {
                        "value": comp.manufacturer
                    }
                ],
                "packer_contact_information": [
                    {
                        "value": comp.packer_details
                    }
                ],
                "main_product_image_locator": [
                    {
                        "media_location": "MAIN_IMAGE.jpg",
                        "marketplace_id": cls.MARKETPLACE_ID
                    }
                ]
            }
        }
        return payload

    @classmethod
    def validate_preflight(cls, listing: CompleteListing) -> List[Dict[str, str]]:
        """Pre-flight listing policy and schema validation before SP-API submission."""
        issues = []
        if len(listing.identity.item_name) > 200:
            issues.append({"severity": "ERROR", "field": "item_name", "message": "Title exceeds 200 characters limit."})
        if len(listing.identity.item_name) < 20:
            issues.append({"severity": "ERROR", "field": "item_name", "message": "Title is too short for Amazon indexing."})
        if listing.offer.standard_price <= 0:
            issues.append({"severity": "ERROR", "field": "standard_price", "message": "Price must be greater than ₹0."})
        if listing.offer.list_price < listing.offer.standard_price:
            issues.append({"severity": "WARNING", "field": "list_price", "message": "MRP (List Price) should be >= Selling Price."})
        if not listing.compliance.hsn_code:
            issues.append({"severity": "ERROR", "field": "hsn_code", "message": "HSN Code is mandatory for Indian GST compliance."})
        if len(listing.description.search_terms.encode("utf-8")) > 249:
            issues.append({"severity": "WARNING", "field": "search_terms", "message": "Backend search terms exceed 249 bytes."})
        return issues

    @classmethod
    def simulate_submission(cls, listing: CompleteListing) -> Dict[str, Any]:
        """Simulates live submission to Amazon SP-API and returns mock response."""
        issues = cls.validate_preflight(listing)
        errors = [i for i in issues if i["severity"] == "ERROR"]

        time.sleep(0.8) # Simulate realistic network round-trip

        if errors:
            return {
                "status": "REJECTED",
                "http_status": 400,
                "submission_id": f"FEED-ERR-{uuid.uuid4().hex[:8].upper()}",
                "errors": errors,
                "warnings": [i for i in issues if i["severity"] == "WARNING"],
                "message": "Submission rejected due to validation errors."
            }

        submission_id = f"FEED-IN-{time.strftime('%Y%m%d')}-{uuid.uuid4().hex[:7].upper()}"
        return {
            "status": "ACCEPTED",
            "http_status": 200,
            "submission_id": submission_id,
            "sku": listing.offer.seller_sku,
            "marketplace_id": cls.MARKETPLACE_ID,
            "submission_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "feed_type": "JSON_LISTINGS_FEED",
            "processing_status": "DONE_SUCCESS",
            "records_processed": 1,
            "records_successful": 1,
            "records_with_error": 0,
            "warnings": [i for i in issues if i["severity"] == "WARNING"],
            "message": f"Successfully published listing SKU [{listing.offer.seller_sku}] to Amazon.in catalog."
        }

    @classmethod
    def generate_automated_script(cls, listing: CompleteListing) -> str:
        """Generates a standalone Python script that the seller can execute with real SP-API credentials."""
        sku = listing.offer.seller_sku
        return f'''"""Standalone Amazon SP-API automated push script for SKU: {sku}"""
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

# Real SP-API credentials
REFRESH_TOKEN = os.getenv("SP_API_REFRESH_TOKEN", "")
CLIENT_ID = os.getenv("SP_API_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("SP_API_CLIENT_SECRET", "")
SELLER_ID = os.getenv("SP_API_SELLER_ID", "MANASVINI_FANCY_IN")
MARKETPLACE_ID = "{cls.MARKETPLACE_ID}"
SKU = "{sku}"

def get_access_token():
    url = "https://api.amazon.com/auth/o2/token"
    data = {{
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }}
    res = requests.post(url, data=data)
    return res.json().get("access_token")

def push_listing():
    token = get_access_token()
    if not token:
        print("Failed to get LWA Access Token. Please verify credentials.")
        return

    url = f"https://sellingpartnerapi-eu.amazon.com/listings/2021-08-01/items/{{SELLER_ID}}/{{SKU}}?marketplaceIds={{MARKETPLACE_ID}}"
    headers = {{
        "x-amz-access-token": token,
        "Content-Type": "application/json"
    }}
    
    with open("listing_payload.json", "r") as f:
        payload = json.load(f).get("listing", {{}})
        
    response = requests.put(url, headers=headers, json=payload)
    print("SP-API Response Status:", response.status_code)
    print("SP-API Response Body:", response.text)

if __name__ == "__main__":
    push_listing()
'''
