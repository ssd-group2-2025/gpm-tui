import typeguard
from dataclasses import dataclass, InitVar, field
from valid8 import validate
import requests
import json
import base64

@typeguard.typechecked()
@dataclass(frozen=True)
class Token:
    access: str
    refresh: str
    init_key: InitVar[object] = field(default=None)
    
    __key = object()
    
    def __post_init__(self, _init_key: object):
        validate("key", _init_key, equals=Token.__key)
            
    @staticmethod
    def __validate_token(name: str, token: object):
        validate(name, token, instance_of=str)

        token_parts = token.split(".")
        validate(name + " parts", token_parts, length=3)

        header_b64, payload_b64, signature_b64 = token_parts

        def decode_base64url(part: str):
            # Add padding if needed
            padding = "=" * (-len(part) % 4)
            try:
                return base64.urlsafe_b64decode(part + padding)
            except Exception:
                raise ValueError(f"Invalid base64 encoding in {name}")

        # Validate header
        header_bytes = decode_base64url(header_b64)
        try:
            header = json.loads(header_bytes)
        except Exception:
            raise ValueError(f"{name} header is not valid JSON")

        validate(name + " header", header, instance_of=dict)
        validate(name + " header.alg", header.get("alg"), instance_of=str)
        validate(name + " header.typ", header.get("typ"), instance_of=str)

        # Validate payload
        payload_bytes = decode_base64url(payload_b64)
        try:
            payload = json.loads(payload_bytes)
        except Exception:
            raise ValueError(f"{name} payload is not valid JSON")

        validate(name + " payload", payload, instance_of=dict)
        validate(name + " payload.token_type", payload.get("token_type"), instance_of=str)
        validate(name + " payload.exp", payload.get("exp"), instance_of=int)

        # Signature: must be non-empty and valid base64url
        validate(name + " signature length", signature_b64, min_len=1)
        decode_base64url(signature_b64)  # will raise if invalid
    
    @staticmethod
    def from_response(response_json: dict):
        access = response_json.get('access')
        Token.__validate_token("access token", access)
        refresh = response_json.get('refresh')
        Token.__validate_token("refresh token", refresh)
        return Token(access, refresh, Token.__key)