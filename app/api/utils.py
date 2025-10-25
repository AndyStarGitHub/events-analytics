from uuid import UUID, uuid4

try:
    from uuid import uuid7 as _uuid7

    def _gen_uuid() -> str:
        return str(_uuid7())
except Exception:
    def _gen_uuid() -> str:
        return str(uuid4())


def extract_request_id_from_headers(headers) -> str:
    incoming = headers.get("x-request-id")
    if incoming:
        try:
            UUID(incoming)
            return incoming
        except ValueError:
            pass
    return _gen_uuid()
