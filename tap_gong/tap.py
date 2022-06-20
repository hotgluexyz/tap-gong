from typing import List
from pendulum import TRANSITION_ERROR

from singer_sdk import Tap, Stream
from singer_sdk import typing as th 
from tap_gong.streams import (
    CallsStream,
    TranscriptStream,
    UsersStream,
    FoldersStream,
    WorkspacesStream
    )

STREAM_TYPES = [
                CallsStream,
                TranscriptStream,
                UsersStream,
                FoldersStream,
                WorkspacesStream
                ]

class TapGong(Tap):
    """Gong tap class."""
    name = "tap-gong"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "auth_token",
            th.StringType,
            required=True,
            description="The token to authenticate against the API service"
        ),
        th.Property(
            "refresh_token",
            th.StringType,
            required=False,
            description="refresh_token"
        ),
        th.Property(
            "start_date",
            th.DateTimeType,
            description="The earliest record date to sync"
        ),
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]

if __name__ == "__main__":
    TapGong.cli()