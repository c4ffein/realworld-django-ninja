from json import decoder, loads
from typing import Any

from ninja.testing import TestClient


class HeaderedClient(TestClient):
    def __init__(self, *args, **kwargs):
        self.headers = kwargs.pop("headers", {})
        super().__init__(*args, **kwargs)

    def request(self, method, path, data={}, json=None, **request_params: Any):
        request_params["headers"] = {**self.headers, **request_params.get("headers", {})}
        r = super().request(method, path, data, json, **request_params)
        try:
            setattr(r, "data", loads(r.content))
        except decoder.JSONDecodeError:
            setattr(r, "data", None)
        except UnicodeDecodeError:
            setattr(r, "data", None)
        return r
