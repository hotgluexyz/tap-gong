"""Stream type classes for tap-gong."""

from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_gong.client import GongStream

class CallsStream(GongStream):
    name = "calls"
    path = "/v2/calls"
    primary_keys = ["id"]
    replication_key = "scheduled"

    schema = th.PropertiesList(
        th.Property("clientUniqueId", th.StringType),
        th.Property("customData",th.StringType),
        th.Property("direction",th.StringType),
        th.Property("duration",th.IntegerType),
        th.Property("id",th.StringType),
        th.Property("isPrivate",th.BooleanType),
        th.Property("language",th.StringType),
        th.Property("media",th.StringType),
        th.Property("meetingUrl",th.StringType),
        th.Property("primaryUserId",th.StringType),
        th.Property("purpose",th.StringType),
        th.Property("scheduled",th.DateTimeType),
        th.Property("scope",th.StringType),
        th.Property("sdrDisposition",th.StringType),
        th.Property("started",th.DateTimeType),
        th.Property("system",th.StringType),
        th.Property("title",th.StringType),
        th.Property("url",th.StringType),
        th.Property("workspaceId",th.StringType),
    ).to_dict()

