from typing import Any, Dict, Optional

from singer_sdk import typing as th

from tap_gong.client import GongStream


class CallsStream(GongStream):
    name = "calls"
    path = "/v2/calls/extensive"
    primary_keys = ["id"]
    replication_key = "scheduled"
    records_jsonpath = "$.calls[*].metaData"
    next_page_token_jsonpath = "$.records.cursor"
    rest_method = "POST"

    schema = th.PropertiesList(
        th.Property("clientUniqueId", th.StringType),
        th.Property("customData", th.StringType),
        th.Property("direction", th.StringType),
        th.Property("duration", th.IntegerType),
        th.Property("id", th.StringType),
        th.Property("isPrivate", th.BooleanType),
        th.Property("language", th.StringType),
        th.Property("media", th.StringType),
        th.Property("meetingUrl", th.StringType),
        th.Property("primaryUserId", th.StringType),
        th.Property("purpose", th.StringType),
        th.Property("scheduled", th.DateTimeType),
        th.Property("scope", th.StringType),
        th.Property("sdrDisposition", th.StringType),
        th.Property("started", th.DateTimeType),
        th.Property("system", th.StringType),
        th.Property("title", th.StringType),
        th.Property("url", th.StringType),
        th.Property("workspaceId", th.StringType),
    ).to_dict()

    def prepare_request_payload(self, context, next_page_token):
        start_date = self.get_starting_time(context)
        start_date = start_date.strftime("%Y-%m-%dT%H:%M:%S%z")
        payload = {"filter": {"fromDateTime": start_date}}
        if next_page_token:
            payload["cursor"] = next_page_token
        return payload

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        return {"callIds": record["id"]}


class TranscriptStream(GongStream):
    name = "transcripts"
    path = "/v2/calls/transcript"
    records_jsonpath = "$.callTranscripts[*]"
    parent_stream_type = CallsStream
    rest_method = "POST"

    schema = th.PropertiesList(
        th.Property("callId", th.StringType),
        th.Property(
            "transcript",
            th.ArrayType(
                th.ObjectType(
                    th.Property("start", th.IntegerType),
                    th.Property("end", th.IntegerType),
                    th.Property("text", th.StringType),
                )
            ),
        ),
    ).to_dict()

    def prepare_request_payload(self, context, next_page_token):
        return {"filter": {"callIds": [context["callIds"]]}}


class UsersStream(GongStream):
    name = "users"
    path = "/v2/users"
    records_jsonpath = "$.users[*]"

    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("emailAddress", th.StringType),
        th.Property("created", th.DateTimeType),
        th.Property("active", th.BooleanType),
        th.Property("emailAliases", th.CustomType({"type": ["array", "string"]})),
        th.Property("firtsName", th.StringType),
        th.Property("lastName", th.StringType),
        th.Property("title", th.StringType),
        th.Property("phoneNumber", th.StringType),
        th.Property("extension", th.StringType),
        th.Property(
            "personalMeetingUrls", th.CustomType({"type": ["array", "string"]})
        ),
        th.Property(
            "settings",
            th.ObjectType(
                th.Property("webConferencesRecorded", th.BooleanType),
                th.Property("preventWebConferenceRecording", th.BooleanType),
                th.Property("telephonyCallsImported", th.BooleanType),
                th.Property("emailsImported", th.BooleanType),
                th.Property("nonRecordedMeetingsImported", th.BooleanType),
            ),
        ),
        th.Property("managedId", th.StringType),
        th.Property("meetingConsentPageUrl", th.StringType),
        th.Property(
            "spokenLanguages",
            th.ArrayType(
                th.ObjectType(
                    th.Property("language", th.StringType),
                    th.Property("primary", th.BooleanType),
                )
            ),
        ),
    ).to_dict()


class WorkspacesStream(GongStream):
    name = "workspaces"
    path = "/v2/workspaces"
    records_jsonpath = "$.workspaces[*]"

    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("name", th.StringType),
        th.Property("description", th.StringType),
    ).to_dict()

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        return {"workspaceId": record["id"]}


class FoldersStream(GongStream):
    name = "folders"
    path = "/v2/library/folders"
    records_jsonpath = "$.folders[*]"
    parent_stream_type = WorkspacesStream

    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("name", th.StringType),
        th.Property("parentFolderId", th.StringType),
        th.Property("createdBy", th.StringType),
        th.Property("updated", th.DateTimeType),
    ).to_dict()

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        params: dict = {}

        params["workspaceId"] = context["workspaceId"]

        if next_page_token:
            params["cursor"] = next_page_token
        if self.replication_key:
            params["fromDateTime"] = self.stream_state.get("replication_key_value")
        return params
