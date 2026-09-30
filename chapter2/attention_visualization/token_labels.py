"""Restore readable text for each position in a token ID sequence."""

import codecs


def _byte_decoder() -> dict[str, int]:
    """Inverse of the GPT-2 byte-to-Unicode alphabet used by byte-level BPE."""
    visible = list(range(ord("!"), ord("~") + 1))
    visible += list(range(ord("¡"), ord("¬") + 1))
    visible += list(range(ord("®"), ord("ÿ") + 1))
    remaining = [value for value in range(256) if value not in visible]
    byte_values = visible + remaining
    unicode_values = visible + list(range(256, 256 + len(remaining)))
    return {chr(value): byte for byte, value in zip(byte_values, unicode_values)}


BYTE_DECODER = _byte_decoder()


def decode_token_labels(
    tokenizer,
    token_ids: list[int],
    *,
    final: bool = True,
) -> list[str]:
    """Decode byte-level tokens in order, assigning a character to its final byte.

    Each returned label still represents exactly one token position. Other
    tokenizer families retain their ordinary per-token decoding behavior.

    Args:
        final: Whether ``token_ids`` is a complete token sequence. ``True``
            (the default) flushes any pending UTF-8 bytes at the end, so a
            genuinely truncated sequence still surfaces a replacement
            character. Streaming/prefix callers pass ``False`` so an
            incomplete trailing character stays buffered until the token that
            completes it arrives instead of being emitted as "�" and then
            duplicated.
    """
    decoder = getattr(getattr(tokenizer, "backend_tokenizer", None), "decoder", None)
    if decoder is None or type(decoder).__name__ != "ByteLevel":
        return [tokenizer.decode([token_id], skip_special_tokens=False) for token_id in token_ids]

    special_ids = set(tokenizer.all_special_ids)
    labels = []
    utf8 = codecs.getincrementaldecoder("utf-8")(errors="replace")
    for token_id in token_ids:
        if token_id in special_ids:
            if labels:
                labels[-1] += utf8.decode(b"", final=True)
            utf8.reset()
            labels.append(tokenizer.decode([token_id], skip_special_tokens=False))
            continue

        raw_token = tokenizer.convert_ids_to_tokens(token_id)
        try:
            raw_bytes = bytes(BYTE_DECODER[char] for char in raw_token)
        except (KeyError, TypeError):
            if labels:
                labels[-1] += utf8.decode(b"", final=True)
            utf8.reset()
            labels.append(tokenizer.decode([token_id], skip_special_tokens=False))
            continue
        labels.append(utf8.decode(raw_bytes, final=False))

    if final and labels:
        labels[-1] += utf8.decode(b"", final=True)
    return labels
