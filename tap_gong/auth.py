"""Gong Authentication."""


from singer_sdk.authenticators import OAuthAuthenticator, SingletonMeta


# The SingletonMeta metaclass makes your streams reuse the same authenticator instance.
# If this behaviour interferes with your use-case, you can remove the metaclass.
class GongAuthenticator(OAuthAuthenticator, metaclass=SingletonMeta):
    """Authenticator class for Gong."""

    @property
    def oauth_request_body(self) -> dict:
        """Define the OAuth request body for the Gong API."""
        return {
            "client_id": self.config["client_id"],
            "response_type": "code",
            "redirect_uri": "https://hotglue.xyz/callback",
            "scope": self.oauth_scopes,
            "state": "hotglue",
        }

    @classmethod
    def create_for_stream(cls, stream) -> "GongAuthenticator":
        return cls(
            stream=stream,
            auth_endpoint="https://app.gong.io/oauth2/authorize",
            oauth_scopes="api:calls:read:transcript api:calls:read:basic api:calls:create api:users:read api:library:read api:workspaces:read",
        )
