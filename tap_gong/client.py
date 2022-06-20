"""REST client handling, including GongStream base class."""

import requests
from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable

from memoization import cached

from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.streams import RESTStream

# from tap_gong.auth import GongAuthenticator
from singer_sdk.authenticators import BearerTokenAuthenticator

class GongStream(RESTStream):
    url_base = "https://api.gong.io"

    records_jsonpath = "$.calls[*]"  # one for each stream 
    next_page_token_jsonpath = "$.records.currentPageNumber"

    # @property
    # @cached
    # def authenticator(self) -> GongAuthenticator:
    #     """Return a new authenticator object."""
    #     return GongAuthenticator.create_for_stream(self)

    @property
    def authenticator(self) -> BearerTokenAuthenticator:

        token = self.config.get("auth_token")
        auth = BearerTokenAuthenticator(self,token = token)

        return auth 

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed."""
        headers = {}
        if "user_agent" in self.config:
            headers["User-Agent"] = self.config.get("user_agent")
        return headers

    def get_next_page_token(
        self, response: requests.Response, previous_token: Optional[Any]
    ) -> Optional[Any]:
        if self.next_page_token_jsonpath:
            all_matches = extract_jsonpath(
                self.next_page_token_jsonpath, response.json()
            )
            first_match = next(iter(all_matches), None)
            next_page_token = first_match
        else:
            next_page_token = response.headers.get("X-Next-Page", None)

        return next_page_token

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        if next_page_token:
            params["page"] = next_page_token
        if self.replication_key:
            params["sort"] = "asc"
            params["order_by"] = self.replication_key
        return params

