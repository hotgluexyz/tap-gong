import json
from datetime import datetime

import requests
from requests.auth import HTTPBasicAuth
from hotglue_singer_sdk.authenticators import OAuthAuthenticator


class OAuth2Authenticator(OAuthAuthenticator):
    """Gong OAuth 2.0 authenticator."""

    @property
    def oauth_request_body(self) -> dict:
        """Return Gong's refresh-token grant payload."""
        return {
            "grant_type": "refresh_token",
            "refresh_token": self._tap._config["refresh_token"],
        }

    def request_auth(self):
        """Return HTTP Basic credentials used to authenticate the token request."""
        return HTTPBasicAuth(self.client_id, self.client_secret)

    def update_access_token_locally(self) -> None:
        """Refresh the Gong access token and persist all updated fields to the config file."""
        request_time = round(datetime.utcnow().timestamp())
        token_response = requests.post(
            self.auth_endpoint,
            params=self.oauth_request_payload,
            auth=self.request_auth(),
        )
        try:
            token_response.raise_for_status()
            self.logger.info("OAuth authorization attempt was successful.")
        except Exception as ex:
            raise RuntimeError(
                f"Failed OAuth login, response was '{token_response.json()}'. {ex}"
            )
        token_json = token_response.json()
        self.access_token = token_json["access_token"]
        self._tap._config["access_token"] = token_json["access_token"]
        self._tap._config["expires_in"] = request_time + token_json["expires_in"]
        self._tap._config["refresh_token"] = token_json["refresh_token"]
        self._tap._config["api_base_url_for_customer"] = token_json.get("api_base_url_for_customer")
        with open(self._tap.config_file, "w") as outfile:
            json.dump(self._tap._config, outfile, indent=4)
