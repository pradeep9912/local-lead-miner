# backend.py
import requests
import pandas as pd
from typing import List, Dict

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
        """
        payload = {
            "textQuery": query,
            "maxResultCount": 20
        }

        try:
            response = requests.post(self.BASE_URL, json=payload, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            return self._normalize_data(data.get("places", []))
            
        except requests.exceptions.RequestException as e:
            print(f"API Request Failed: {e}")
            return pd.DataFrame()

    def _normalize_data(self, places: List[Dict]) -> pd.DataFrame:
        """
        Internal method to clean and structure the raw JSON data.
        """
        normalized = []
        
        for place in places:
            if place.get("businessStatus") == "CLOSED_PERMANENTLY":
                continue

            website = place.get("websiteUri")
            
            normalized.append({
                "Business Name": place.get("displayName", {}).get("text", "N/A"),
                "Address": place.get("formattedAddress", "N/A"),
                "Phone": place.get("nationalPhoneNumber", "N/A"),
                # UPDATE 2: Extract the rating count (default to 0 if missing)
                "Ratings Count": place.get("userRatingCount", 0),
                "Has Website": "Yes" if website else "No",
                "Website URL": website if website else ""
            })
            
        return pd.DataFrame(normalized)