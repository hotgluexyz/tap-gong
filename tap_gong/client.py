from typing import Any, Dict, Optional

from memoization import cached
from pendulum import parse
from singer_sdk.streams import RESTStream

from tap_gong.auth import OAuth2Authenticator


class GongStream(RESTStream):

    url_base = "https://api.gong.io"
    records_jsonpath = "$.calls[*]"
    next_page_token_jsonpath = "$.records.currentPageNumber"

    @cached
    def get_starting_time(self, context):
        start_date = parse(self.config.get("start_date"))
        rep_key = self.get_starting_timestamp(context)
        return rep_key or start_date

    @property
    def authenticator(self) -> OAuth2Authenticator:
        """Return a new authenticator object."""
        url = f"{self.url_base}/oauth2/generate-token"
        return OAuth2Authenticator(self, self._tap.config, url)

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
