# tap-gong

`tap-gong` is a Singer tap for Gong.

Built with the [Hotglue Singer SDK](https://github.com/hotglueHQ/HotglueSingerSDK) for Singer Taps.

## Installation

```bash
pipx install tap-gong
```

## Configuration

### Accepted Config Options

| Setting | Required | Default | Description |
|---|---|---|---|
| `access_token` | Yes | — | Gong OAuth2 access token |
| `client_id` | Yes | — | Gong OAuth2 client ID |
| `client_secret` | Yes | — | Gong OAuth2 client secret |
| `refresh_token` | No | — | Gong OAuth2 refresh token. Required when using token refresh. Updated automatically after each refresh. |
| `start_date` | No | — | Earliest date to sync records from, in ISO 8601 format (e.g. `2024-01-01T00:00:00Z`) |
| `api_base_url_for_customer` | No | `https://api.gong.io` | Override the Gong API base URL (set automatically on token refresh) |
| `wait_hour` | No | `1` | Maximum number of hours to wait when Gong returns a rate-limit response before raising an error |

A full list of supported settings and capabilities is also available by running:

```bash
tap-gong --about
```

### Sample `config.json`

```json
{
  "client_id": "your-client-id",
  "client_secret": "your-client-secret",
  "access_token": "your-access-token",
  "refresh_token": "your-refresh-token",
  "start_date": "2024-01-01T00:00:00Z"
}
```

### Configure using environment variables

This Singer tap will automatically import any environment variables within the working directory's
`.env` if the `--config=ENV` is provided, such that config values will be considered if a matching
environment variable is set either in the terminal context or in the `.env` file.

### Source Authentication and Authorization

- [ ] `Developer TODO:` If your tap requires special access on the source system, or any special authentication requirements, provide those here.

## Usage

You can easily run `tap-gong` by itself or in a pipeline using [Meltano](https://meltano.com/).

### Executing the Tap Directly

```bash
tap-gong --version
tap-gong --help
tap-gong --config CONFIG --discover > ./catalog.json
```

## Developer Resources

### Initialize your Development Environment

```bash
pipx install poetry
poetry install
```

### Create and Run Tests

Create tests within the `tap_gong/tests` subfolder and
  then run:

```bash
poetry run pytest
```

You can also test the `tap-gong` CLI interface directly using `poetry run`:

```bash
poetry run tap-gong --help
```

### Testing with [Meltano](https://www.meltano.com)

_**Note:** This tap will work in any Singer environment and does not require Meltano.
Examples here are for convenience and to streamline end-to-end orchestration scenarios._

Your project comes with a custom `meltano.yml` project file already created. Open the `meltano.yml` and follow any _"TODO"_ items listed in
the file.

Next, install Meltano (if you haven't already) and any needed plugins:

```bash
# Install meltano
pipx install meltano
# Initialize meltano within this directory
cd tap-gong
meltano install
```

Now you can test and orchestrate using Meltano:

```bash
# Test invocation:
meltano invoke tap-gong --version
# OR run a test `elt` pipeline:
meltano elt tap-gong target-jsonl
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to 
develop your own taps and targets.
