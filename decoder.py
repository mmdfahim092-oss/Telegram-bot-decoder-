"""Static decoder for common JavaScript/Base64-obfuscated HTML wrappers.

This module treats all input as text. It never executes JavaScript, opens URLs,
loads remote resources, or evaluates decoded output.
"""
from __future__ import annotations

import base64
import binascii
import json
import re
from dataclasses import dataclass


@dataclass
class DecodeResult:
    text: str
    layers: int
    notes: list[str]


def _decode_b64(value: str) -> str | None:
    value = re.sub(r"\s+", "", value)
    if not value or not re.fullmatch(r"[A-Za-z0-9+/]*={0,2}", value):
        return None
    value += "=" * ((-len(value)) % 4)
    try:
        raw = base64.b64decode(value, validate=True)
        # decodeURIComponent(escape(atob(...))) convention means UTF-8 text.
        return raw.decode("utf-8")
    except (binascii.Error, UnicodeDecodeError, ValueError):
        return None


def _decode_indexed_array(text: str) -> str | None:
    """Decode patterns like _c=[{i:...,d:'...'}, ...]; then join by i."""
    match = re.search(r"\bvar\s+_c\s*=\s*(\[.*?\])\s*;\s*var\s+_res\b", text, re.S)
    if not match:
        return None
    try:
        entries = json.loads(match.group(1))
        if not isinstance(entries, list) or not entries:
            return None
        indexed: dict[int, str] = {}
        for item in entries:
            if not isinstance(item, dict) or not isinstance(item.get("i"), int) or not isinstance(item.get("d"), str):
                return None
            indexed[item["i"]] = item["d"]
        combined = "".join(indexed.get(i, "") for i in range(max(indexed) + 1))
        decoded = _decode_b64(combined)
        return decoded
    except (json.JSONDecodeError, TypeError, ValueError):
        return None


def _decode_string_assignment(text: str) -> str | None:
    """Decode concatenated quoted Base64 assigned to a JS variable."""
    # Limit the match to a single assignment ending at semicolon; supports
    # `var x='abc' + 'def';` and newline formatting.
    for match in re.finditer(r"\b(?:var|let|const)\s+[A-Za-z_$][\w$]*\s*=\s*(.*?);", text, re.S):
        rhs = match.group(1)
        pieces = re.findall(r"(['\"])(.*?)\1", rhs, re.S)
        if not pieces:
            continue
        # Only accept assignments made up of quoted strings, plus signs and whitespace.
        residue = re.sub(r"(['\"])(.*?)\1", "", rhs, flags=re.S)
        if re.sub(r"[+\s()]", "", residue):
            continue
        candidate = "".join(piece[1] for piece in pieces)
        decoded = _decode_b64(candidate)
        if decoded is not None and ("<html" in decoded.lower() or "<!doctype" in decoded.lower() or "<script" in decoded.lower()):
            return decoded
    return None


def decode_html(source: str, max_layers: int = 8) -> DecodeResult:
    current = source
    notes: list[str] = []
    layers = 0
    for _ in range(max_layers):
        decoded = _decode_indexed_array(current)
        method = "indexed Base64 chunks" if decoded is not None else ""
        if decoded is None:
            decoded = _decode_string_assignment(current)
            method = "concatenated Base64 string" if decoded is not None else ""
        if decoded is None or decoded == current:
            break
        current = decoded
        layers += 1
        notes.append(f"Layer {layers}: decoded {method} (text only; not executed).")
    if layers == 0:
        notes.append("No supported wrapper found. The file was left unchanged.")
    return DecodeResult(current, layers, notes)
  
