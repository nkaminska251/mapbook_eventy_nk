from __future__ import annotations

import os

import requests

from config import GOOGLE_MAPS_API_KEY_ENV


def get_coordinates(location: str) -> list[float]:
    if not location:
        return []

    api_key = os.getenv(GOOGLE_MAPS_API_KEY_ENV)
    if not api_key:
        return []

    try:
        response = requests.get(
            "https://maps.googleapis.com/maps/api/geocode/json",
            params={
                "address": location.strip(),
                "key": api_key,
                "language": "pl",
                "region": "pl",
            },
            timeout=10,
        )
        response.raise_for_status()

        data = response.json()
        if data.get("status") != "OK" or not data.get("results"):
            return []

        location_data = data["results"][0]["geometry"]["location"]
        return [float(location_data["lat"]), float(location_data["lng"])]
    except Exception:
        return []