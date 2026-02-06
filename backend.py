# backend.py
import logging
import requests
import pandas as pd
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PlacesService:
    """
    Service layer to interact with Google Places API (New Version).
    """
    
    BASE_URL = "https://places.googleapis.com/v1/places:searchText"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            # UPDATE 1: Added 'places.userRatingCount' to the request mask
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.nationalPhoneNumber,places.websiteUri,places.businessStatus,places.userRatingCount"
        }

    def fetch_leads(self, query: str) -> pd.DataFrame:
        """
        Fetches business data and returns a cleaned Pandas DataFrame.
        
        Args:
            query: Search query string for Google Places API
            
        Returns:
            DataFrame with normalized business data or empty DataFrame on error
        """
        if not query or not query.strip():
            logger.warning("Empty search query provided")
            return pd.DataFrame()
        
        payload = {
            "textQuery": query,
            "maxResultCount": 20
        }

        try:
            response = requests.post(
                self.BASE_URL, 
                json=payload, 
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            logger.info(f"Successfully fetched {len(data.get('places', []))} results")
            
            return self._normalize_data(data.get("places", []))
            
        except requests.exceptions.Timeout:
            logger.error("API request timed out")
            return pd.DataFrame()
        except requests.exceptions.RequestException as e:
            logger.error(f"API Request Failed: {e}")
            return pd.DataFrame()

    def _normalize_data(self, places: List[Dict]) -> pd.DataFrame:
        """
        Internal method to clean and structure the raw JSON data.
        
        Args:
            places: List of place dictionaries from Google Places API
            
        Returns:
            Normalized DataFrame with structured business information
        """
        normalized = []
        
        for place in places:
            if place.get("businessStatus") == "CLOSED_PERMANENTLY":
                continue

            website = place.get("websiteUri")
            
            # Safely extract nested displayName
            display_name = place.get("displayName", {})
            business_name = display_name.get("text", "N/A") if isinstance(display_name, dict) else "N/A"
            
            normalized.append({
                "Business Name": business_name,
                "Address": place.get("formattedAddress", "N/A"),
                "Phone": place.get("nationalPhoneNumber", "N/A"),
                "Ratings Count": place.get("userRatingCount", 0),
                "Has Website": "Yes" if website else "No",
                "Website URL": website if website else ""
            })
        
        logger.info(f"Normalized {len(normalized)} businesses")
        return pd.DataFrame(normalized)