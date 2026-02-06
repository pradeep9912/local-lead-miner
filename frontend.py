# frontend.py
import streamlit as st
import os
from dotenv import load_dotenv
from backend import PlacesService

load_dotenv()

def validate_input(text: str, field_name: str) -> bool:
    """
    Validate user input to ensure it's not empty.
    
    Args:
        text: Input text to validate
        field_name: Name of the field for error message
        
    Returns:
        True if valid, False otherwise
    """
    if not text or not text.strip():
        st.error(f"{field_name} cannot be empty.")
        return False
    return True

def main():
    """
    Main Streamlit application for Google Maps Lead Mining.
    Allows users to search for businesses and extract lead information.
    """
    st.set_page_config(page_title="Lead Extractor Pro", layout="wide")
    
    st.title("📍 Google Maps Lead Miner")

    # --- Sidebar: Configuration ---
    with st.sidebar:
        st.header("Configuration")
        
        api_key = os.getenv("GOOGLE_API_KEY")
        
        if api_key:
            st.success("API Key loaded safely from environment.")
        else:
            api_key = st.text_input("Enter Google Maps API Key", type="password")
        
        st.divider()
        
        area = st.text_input("Target Area", placeholder="e.g., Thoraipakkam, Chennai")
        biz_type = st.text_input("Business Category", placeholder="e.g., Gym")
        
        run_btn = st.button("Extract Data", type="primary")

    # --- Main Execution ---
    if run_btn:
        if not api_key:
            st.error("Missing API Key. Please check your .env file.")
            return
        
        if not validate_input(area, "Target Area") or not validate_input(biz_type, "Business Category"):
            return

        service = PlacesService(api_key)
        search_query = f"{biz_type} in {area}"

        with st.spinner(f"Searching for '{search_query}'..."):
            df = service.fetch_leads(search_query)

        if not df.empty:
            st.success(f"Found {len(df)} businesses.")
            
            tab1, tab2 = st.tabs(["📋 All Businesses", "🎯 Leads (No Website)"])
            
            # TAB 1: Show everything (Good for checking data)
            with tab1:
                st.dataframe(df, use_container_width=True)

            # TAB 2: Clean Leads View (No empty columns)
            with tab2:
                leads = df[df['Has Website'] == "No"]
                
                if not leads.empty:
                    # UPDATE: Drop the useless columns for this specific view
                    clean_leads = leads.drop(columns=["Website URL", "Has Website"])
                    
                    st.dataframe(clean_leads, use_container_width=True)
                    
                    # CSV Download Button
                    csv = clean_leads.to_csv(index=False).encode('utf-8')
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