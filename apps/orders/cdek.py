import requests
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class CDEKClient:
    """CDEK API client for shipping calculations"""

    def __init__(self):
        self.account = settings.CDEK_ACCOUNT
        self.secure_password = settings.CDEK_SECURE_PASSWORD
        self.auth_url = "https://api.cdek.ru/v2/oauth/token"
        self.api_url = "https://api.cdek.ru/v2/calculator/tarifflist"
        self.token = None

    def _get_auth_token(self):
        """Get authentication token from CDEK API"""
        if self.token:
            return self.token

        auth_data = {
            "grant_type": "client_credentials",
            "client_id": self.account,
            "client_secret": self.secure_password,
        }

        try:
            response = requests.post(self.auth_url, data=auth_data)
            if response.status_code == 200:
                self.token = response.json().get("access_token")
                return self.token
        except requests.exceptions.RequestException:
            pass

        return None

    def calculate_shipping(
        self, from_location, to_location, package_size, package_weight
    ):
        """Calculate shipping cost"""
        token = self._get_auth_token()
        if not token:
            return None

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        payload = {
            "type": 1,  # Delivery type (1 - door-to-door)
            "currency": 1,  # RUB
            "lang": "rus",
            "from_location": {"code": from_location},  # Sender city code
            "to_location": {"code": to_location},  # Receiver city code
            "packages": [
                {
                    "height": package_size["height"],
                    "length": package_size["length"],
                    "width": package_size["width"],
                    "weight": package_weight,
                }
            ],
        }

        try:
            response = requests.post(self.api_url, json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                # Find the cheapest tariff
                tariffs = data.get("tariff_codes", [])
                if tariffs:
                    cheapest = min(
                        tariffs, key=lambda x: x.get("delivery_sum", float("inf"))
                    )
                    return {
                        "cost": cheapest.get("delivery_sum"),
                        "min_days": cheapest.get("period_min"),
                        "max_days": cheapest.get("period_max"),
                    }
        except requests.exceptions.RequestException:
            pass

        return None

    def get_pvz_list(self, city_code):
        """Get list of pickup points for a city"""
        token = self._get_auth_token()
        if not token:
            return None

        headers = {"Authorization": f"Bearer {token}"}

        try:
            url = f"https://api.cdek.ru/v2/deliverypoints?city_code={city_code}"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
        except requests.exceptions.RequestException:
            pass

        return None
