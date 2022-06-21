from typing import Any, Dict, Optional, Union

from singer.schema import Schema
from singer_sdk.authenticators import BearerTokenAuthenticator
from singer_sdk.plugin_base import PluginBase as TapBaseClass
from singer_sdk.streams import RESTStream

from tap_gong.auth import GongAuthenticator


class GongStream(RESTStream):
    def __init__(
        self,
        tap: TapBaseClass,
        name: Optional[str] = None,
        schema: Optional[Union[Dict[str, Any], Schema]] = None,
        path: Optional[str] = None,
    ) -> None:
        super().__init__(tap, name, schema, path)
        # self.access_token = self.config["auth_token"]

    url_base = "https://api.gong.io"
    records_jsonpath = "$.calls[*]"
    next_page_token_jsonpath = "$.records.currentPageNumber"

    # @property
    # @cached
    # def authenticator(self) -> GongAuthenticator:
    #     """Return a new authenticator object."""
    #     return GongAuthenticator.create_for_stream(self)

    @property
    def authenticator(self) -> BearerTokenAuthenticator:

        token = self.config.get("auth_token")
        auth = BearerTokenAuthenticator(self, token=token)

        return auth

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        params: dict = {}
        if next_page_token:
            params["cursor"] = next_page_token

        replication_key_value = self.stream_state.get("replication_key_value")
        start_date = self.config.get("start_date")
        if replication_key_value:
            params["fromDateTime"] = replication_key_value
        elif start_date:
            params["fromDateTime"] = start_date
        return params
