"""Step 5 UI: Automated Upload, Flat File Generator & SP-API Push Engine."""

import streamlit as st
import json
import pandas as pd
from typing import Dict, Any

from export.flat_file_generator import AmazonFlatFileGenerator
from export.zip_packager import ZipBundlePackager
from export.sp_api_mock import AmazonSPAPIMockEngine
from ui.live_pdp_preview import render_amazon_pdp_preview


def render_step5_export_publish(session_state):
    """Renders the Live PDP Upload Preview, Export Engine, and SP-API push simulation."""
    st.markdown("""
    <div class="amazon-card">
        <div class="amazon-card-header">
            <div>
                <h3 class="amazon-card-title">Step 5: Pre-Upload Visual Inspection & Export Engine</h3>
                <div style="font-size: 0.85rem; color: #565959;">
                    Visually inspect how your product appears to Amazon shoppers (Live PDP Preview)
                    and verify flat file data before downloading or pushing directly to Amazon.
                </div>
            </div>
            <span class="badge-success">Ready for Review & Publish</span>
        </div>
    """, unsafe_allow_html=True)

    listing = session_state.get("complete_listing")
    if not listing:
        st.warning("Please review and confirm your listing details in Step 4 before exporting.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # Section 1: Pre-Upload Inspection Modes (Live PDP vs Raw Flat File Table)
    st.markdown("### 🔍 Pre-Upload Inspection")
    view_mode = st.radio(
        "Choose Preview Mode:",
        options=["🛍️ Live Amazon Buyer Page Preview (PDP Simulation)", "📊 Amazon Flat File Upload Table", "📄 JSON Metadata Spec"],
        horizontal=True,
        key="step5_preview_mode_selector"
    )

    if view_mode == "🛍️ Live Amazon Buyer Page Preview (PDP Simulation)":
        render_amazon_pdp_preview(
            listing=listing,
            processed_images=session_state.processed_images,
            raw_images=session_state.raw_images
        )
    elif view_mode == "📊 Amazon Flat File Upload Table":
        st.markdown("#### Amazon Seller Central Upload Columns & Values")
        flat_dict = AmazonFlatFileGenerator.generate_row_dict(listing)
        df_preview = pd.DataFrame([
            {"Technical Column": col, "Amazon Field Name": label, "Listing Value": flat_dict.get(col, "")}
            for col, label in AmazonFlatFileGenerator.COLUMNS
        ])
        st.dataframe(df_preview, use_container_width=True, height=420)
    else:
        st.markdown("#### Complete Listing JSON Payload")
        st.json(listing.model_dump())

    st.markdown("---")

    # Section 2: Summary Metrics
    st.markdown("### 📦 Publish & Download Actions")
    summary = listing.get_summary_dict()
    sum_cols = st.columns(4)
    sum_cols[0].metric("Seller SKU", summary["SKU"])
    sum_cols[1].metric("Selling Price", summary["Price"], summary["Discount"])
    sum_cols[2].metric("MRP", summary["MRP"])
    sum_cols[3].metric("HSN Code", summary["HSN Code"], "GST 18%")

    st.markdown("---")

    # Section 3: Download Options (Flat File & ZIP Bundle)
    st.markdown("#### 1. Download Inventory Files & Image Assets")
    col_dl_zip, col_dl_tsv, col_dl_csv = st.columns(3)

    # 1. Complete ZIP Bundle (5 Images + Flat Files + JSON + Report)
    with col_dl_zip:
        st.markdown("**Complete Amazon Listing ZIP Bundle**")
        st.caption("Includes all 5 white-background 2000x2000px images, TSV flat file, CSV, JSON payload & Report.")

        zip_bytes = ZipBundlePackager.create_bundle(
            listing=listing,
            processed_images=session_state.processed_images
        )

        st.download_button(
            label="Download Complete ZIP Bundle (.zip)",
            data=zip_bytes,
            file_name=f"{listing.offer.seller_sku}_Amazon_Listing_Bundle.zip",
            mime="application/zip",
            type="primary",
            use_container_width=True,
            key="btn_dl_zip"
        )

    # 2. Amazon Flat File TSV
    with col_dl_tsv:
        st.markdown("**Amazon Inventory Flat File (.tsv / .txt)**")
        st.caption("Official Tab-Delimited format with 3-row headers for Amazon 'Add Products via Upload'.")

        tsv_data = AmazonFlatFileGenerator.generate_tsv(listing)
        st.download_button(
            label="Download Flat File (.tsv)",
            data=tsv_data,
            file_name=f"{listing.offer.seller_sku}_Inventory_FlatFile.tsv",
            mime="text/tab-separated-values",
            type="secondary",
            use_container_width=True,
            key="btn_dl_tsv"
        )

    # 3. Spreadsheets CSV
    with col_dl_csv:
        st.markdown("**Spreadsheet Catalog File (.csv)**")
        st.caption("Comma-separated values format for Microsoft Excel, Numbers, and Google Sheets.")

        csv_data = AmazonFlatFileGenerator.generate_csv(listing)
        st.download_button(
            label="Download Spreadsheet (.csv)",
            data=csv_data,
            file_name=f"{listing.offer.seller_sku}_Catalog.csv",
            mime="text/csv",
            type="secondary",
            use_container_width=True,
            key="btn_dl_csv"
        )

    st.markdown("---")

    # Section 4: Direct Amazon Selling Partner API (SP-API) Push Simulation
    st.markdown("#### 2. Amazon SP-API Direct Publish Simulation")
    st.caption("Directly simulates the Amazon SP-API Listings Items API (<code>PUT /listings/2021-08-01/items/{sellerId}/{sku}</code>) with automated validation.")

    col_api_btn, col_api_info = st.columns([1.5, 2.5])
    with col_api_btn:
        push_clicked = st.button(
            "Push Listing via Amazon SP-API",
            type="primary",
            use_container_width=True,
            key="btn_sp_api_push"
        )

    with col_api_info:
        st.markdown(f"**Target Endpoint:** `https://sellingpartnerapi-eu.amazon.com/listings/2021-08-01/items/MANASVINI_FANCY_IN/{listing.offer.seller_sku}`")

    if push_clicked:
        with st.spinner("Dispatching encrypted SP-API Listings Items payload to Amazon.in catalog..."):
            sim_res = AmazonSPAPIMockEngine.simulate_submission(listing)
            session_state.sp_api_response = sim_res

            if sim_res["status"] == "ACCEPTED":
                st.balloons()
                st.success(f"Listing Successfully Pushed to Amazon.in! Feed ID: {sim_res['submission_id']}")
            else:
                st.error("SP-API Pre-flight Validation Rejected the listing. Check errors below.")

    if session_state.get("sp_api_response"):
        res = session_state.sp_api_response
        st.markdown(f"""
        <div style="background:#131921; color:#00FF66; padding:15px; border-radius:8px; font-family:monospace; font-size:0.85rem; margin-top:10px;">
            <b>AMAZON SP-API GATEWAY RESPONSE [HTTP {res.get('http_status', 200)} OK]</b><br>
            ----------------------------------------------------------------------<br>
            Submission ID   : {res.get('submission_id')}<br>
            SKU             : {res.get('sku')}<br>
            Marketplace ID  : {res.get('marketplace_id')} (Amazon India)<br>
            Feed Status     : {res.get('processing_status')}<br>
            Records Done    : {res.get('records_successful')} / {res.get('records_processed')} Successful<br>
            Timestamp       : {res.get('submission_timestamp')}<br>
            Message         : {res.get('message')}<br>
            ----------------------------------------------------------------------<br>
            LISTING IS LIVE IN CATALOG SUBMISSION QUEUE
        </div>
        """, unsafe_allow_html=True)

    # Section 5: Developer & Headless Automation Script
    with st.expander("View SP-API JSON Payload & Automated CLI Python Script"):
        tab_json, tab_py = st.tabs(["SP-API JSON Payload", "Automated Python Push Script"])
        with tab_json:
            sp_payload = AmazonSPAPIMockEngine.generate_listings_item_payload(listing)
            st.json(sp_payload)
        with tab_py:
            py_script = AmazonSPAPIMockEngine.generate_automated_script(listing)
            st.code(py_script, language="python")
            st.download_button(
                "Download push_sp_api.py",
                data=py_script,
                file_name="push_sp_api.py",
                mime="text/x-python",
                key="btn_dl_script"
            )

    st.markdown("</div>", unsafe_allow_html=True)
