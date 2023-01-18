from io import BytesIO
from json import loads, JSONDecodeError, dumps
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from typing import NamedTuple


DEFAULT_CHARSET = "utf-8"
DEFAULT_CHUNK_SIZE = 1024
DEFAULT_TIMEOUT = 10


class Response(NamedTuple):
    body: bytes
    headers: dict
    status: int
    error_count: int = 0
    chunk_size: int = DEFAULT_CHUNK_SIZE

    def json(self):
        try:
            return loads(
                self.body.decode(self.headers.get("Content-Type", DEFAULT_CHARSET))
            )
        except JSONDecodeError:
            return self.body

    def stream(self):
        for i in range(0, len(self.body), self.chunk_size):
            yield self.body[i : i + self.chunk_size]

    def get_raw(self):
        return BytesIO(self.body)


def request(
    url: str,
    data: dict = None,
    params: dict = None,
    headers: dict = None,
    method: str = "GET",
    data_as_json: bool = True,
    error_count: int = 0,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    timeout=DEFAULT_TIMEOUT,
) -> Response:

    method = method.upper()

    data = data or {}
    params = params or {}
    headers = headers or {}

    headers = {"Accept": "application/json", **headers}

    request_data = None

    if method == "GET":
        params = {**params, **data}
        data = None

    if params:
        url += "?" + urlencode(params)

    if data:
        if data_as_json:
            request_data = dumps(data).encode()
            headers["Content-Type"] = "application/json; charset=UTF-8"
        else:
            request_data = urlencode(data).encode()

    req = Request(
        url, data=request_data, headers=headers, method=method, unverifiable=True
    )

    try:
        with urlopen(
            req, timeout=timeout, cadefault=False
        ) as res:
            body = res.read()
            headers = dict(res.headers)
            status = res.status
            return Response(body, headers, status, error_count, chunk_size)

    except HTTPError as e:
        return Response(
            body=str(e.reason),
            headers=dict(e.headers),
            status=e.code,
            error_count=error_count + 1,
        )
