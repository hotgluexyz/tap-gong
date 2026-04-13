from typing import Any, Dict, Optional

from memoization import cached
from pendulum import parse
from hotglue_singer_sdk.streams import RESTStream

from tap_gong.auth import OAuth2Authenticator
import requests
from hotglue_singer_sdk.exceptions import FatalAPIError, RetriableAPIError

class GongStream(RESTStream):

    records_jsonpath = "$.calls[*]"
    next_page_token_jsonpath = "$.records.currentPageNumber"

    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        return self.config.get("api_base_url_for_customer", "https://api.gong.io")

    @cached
    def get_starting_time(self, context):
        start_date = parse(self.config.get("start_date"))
        rep_key = self.get_starting_timestamp(context)
        return rep_key or start_date

    @property
    def authenticator(self) -> OAuth2Authenticator:
        """Return a new authenticator object."""
        url = "https://app.gong.io/oauth2/generate-customer-token"
        return OAuth2Authenticator(self, auth_endpoint=url)

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
    
    def validate_response(self, response: requests.Response) -> None:

        # Configurable maximum wait time in hours
        max_wait_time_hours = self.config.get("wait_hour",1)
        #Not getting header with Retry-After for now. Adding check for it.
        if "Retry-After" in response.headers:
            retry_after = response.headers['Retry-After']
            wait_time = int(retry_after)
            if wait_time > (max_wait_time_hours * 3600):
                raise Exception(f"Daily limit exceeded. Wait time ({wait_time} seconds) exceeds {max_wait_time_hours} hour(s)")

        if (
            response.status_code in self.extra_retry_statuses
            or 500 <= response.status_code < 600
        ):
            msg = self.response_error_message(response)
            raise RetriableAPIError(msg, response)
        elif 400 <= response.status_code < 500:
            msg = self.response_error_message(response)
            raise FatalAPIError(msg)
