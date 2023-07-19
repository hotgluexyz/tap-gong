from typing import Any, Dict, Optional, Iterable

from memoization import cached
from pendulum import parse
from singer_sdk.streams import RESTStream

from tap_gong.auth import OAuth2Authenticator
import requests
from singer_sdk.exceptions import FatalAPIError, RetriableAPIError
from singer_sdk.helpers.jsonpath import extract_jsonpath

class GongStream(RESTStream):

    url_base = "https://api.gong.io"
    records_jsonpath = "$.calls[*]"
    next_page_token_jsonpath = "$.records.currentPageNumber"
    end_job = False
    @cached
    def get_starting_time(self, context):
        start_date = parse(self.config.get("start_date"))
        rep_key = self.get_starting_timestamp(context)
        return rep_key or start_date

    @property
    def authenticator(self) -> OAuth2Authenticator:
        """Return a new authenticator object."""
        url = "https://app.gong.io/oauth2/generate-token"
        return OAuth2Authenticator(self, self._tap.config, url)
    
    def check_retry_after(self,response):
        # Configurable maximum wait time in hours
        max_wait_time_hours = self.config.get("wait_hour",1)
        #Not getting header with Retry-After for now. Adding check for it.
        if "Retry-After" in response.headers:
            retry_after = response.headers['Retry-After']
            wait_time = int(retry_after)
            #End the job gracefully if wait time is longer than wait_hour
            if wait_time > (max_wait_time_hours * 3600):
                self.end_job = True     

    def get_next_page_token(
        self, response: requests.Response, previous_token: Optional[Any]
    ) -> Any:
        
        if self.end_job:
            return None
        
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

        self.check_retry_after(response)
        if (
            response.status_code in self.extra_retry_statuses
            or 500 <= response.status_code < 600
        ):
            msg = self.response_error_message(response)
            raise RetriableAPIError(msg, response)
        elif 400 <= response.status_code < 500:
            msg = self.response_error_message(response)
            raise FatalAPIError(msg)

       
