# frontend.py
import streamlit as st
import os
from dotenv import load_dotenv
from backend import PlacesService

# 1. Load the secrets from your .env file
load_dotenv()

def main():
    st.set_page_config(page_title="Lead Extractor Pro", layout="wide")
    
    st.title("📍 Google Maps Lead Miner")

    # --- Sidebar: Configuration ---
    with st.sidebar:
        st.header("Configuration")
        
        # Security Check: Try to get key from .env first
        api_key = os.getenv("GOOGLE_API_KEY")
        
        if api_key:
            st.success("API Key loaded safely from environment.")
        else:
            # Fallback if .env is missing
            api_key = st.text_input("Enter Google Maps API Key", type="password")
        
        st.divider()
        
        area = st.text_input("Target Area", "Thoraipakkam, Chennai")
        biz_type = st.text_input("Business Category", "Gym")
        
        run_btn = st.button("Extract Data", type="primary")

    # --- Main Execution ---
    if run_btn:
        if not api_key:
            st.error("Missing API Key. Please check your .env file.")
            return

        service = PlacesService(api_key)
        search_query = f"{biz_type} in {area}"

        with st.spinner(f"Searching for '{search_query}'..."):
            df = service.fetch_leads(search_query)

        if not df.empty:
            st.success(f"Found {len(df)} businesses.")
            
            # Create Tabs
            tab1, tab2 = st.tabs(["📋 All Businesses", "🎯 No Website (Leads)"])
            
            with tab1:
               st.dataframe(df, use_container_width=True)

            with tab2:
                # FILTER LOGIC: Only show rows where 'Has Website' is 'No'
                leads = df[df['Has Website'] == "No"]
                
                if not leads.empty:
                    st.dataframe(leads, use_container_width=True)
                    
                    # CSV Download Button
                    csv = leads.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "Download Leads CSV",
                        csv,
                        "leads.csv",
                        "text/csv"
                    )
                else:
                    st.info("All businesses found have websites!")
        else:
            st.warning("No results found. Try a broader search term.")

if __name__ == "__main__":
    main()