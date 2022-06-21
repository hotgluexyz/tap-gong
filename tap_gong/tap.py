from typing import List

from pendulum import TRANSITION_ERROR
from singer_sdk import Stream, Tap
from singer_sdk import typing as th

from tap_gong.streams import (
    CallsStream,
    FoldersStream,
    TranscriptStream,
    UsersStream,
    WorkspacesStream,
)

STREAM_TYPES = [
    CallsStream,
    TranscriptStream,
    UsersStream,
    FoldersStream,
    WorkspacesStream,
]


class TapGong(Tap):
    """Gong tap class."""

    def __init__(
        self,
        config=None,
        catalog=None,
        state=None,
        parse_env_config=False,
        validate_config=True,
    ) -> None:
        self.config_file = config[0]
        super().__init__(config, catalog, state, parse_env_config, validate_config)

    name = "tap-gong"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "access_token",
            th.StringType,
            required=True,
        ),
        th.Property(
            "refresh_token",
            th.StringType,
            required=False,
        ),
        th.Property("start_date", th.DateTimeType, required=False),
        th.Property("client_id", th.StringType, required=True),
        th.Property("client_secret", th.StringType, required=True),
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]


if __name__ == "__main__":
    TapGong.cli()
