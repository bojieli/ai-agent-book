"""Regression tests for end-of-stream UTF-8 flushing in ``generate_with_streaming``.

A Qwen3 ByteLevel tokenizer can split a single UTF-8 character across several
tokens. While generation is running, the method decodes each growing prefix with
``final=False``, which intentionally leaves a trailing incomplete character
buffered. Once generation actually ends -- EOS, stop string or
``max_new_tokens`` -- the returned text must be rebuilt from the complete token
ID sequence with ``final=True`` so those bytes surface instead of being dropped.

The tests drive the real ``ReActAttentionAgent.generate_with_streaming`` method
with a scripted model, so they exercise the actual exit paths rather than a
re-implementation of the loop.
"""

import types
import unittest

import torch
from main import ReActAttentionAgent
from token_labels import BYTE_DECODER

BYTE_ENCODER = {byte: char for char, byte in BYTE_DECODER.items()}

EOS_ID = 999
SPECIAL_ID = 1000
STOP_ID = 1001  # special token whose text is a stop string, not the EOS id

# Byte splits observed with Qwen3's ByteLevel tokenizer.
BEIJING = bytes.fromhex("E5 8C 97 E4 BA AC")  # 北京
INCOMPLETE_TIAN_PREFIX = bytes.fromhex("E5 A4")  # first two bytes of 天
SPACE_AND_PARTIAL_TIAN = bytes.fromhex("20 E5 A4")  # " " + first two bytes of 天
PARTIAL_TIAN = bytes.fromhex("A9")  # final byte of 天
TIAN_AND_PARTIAL_QI = bytes.fromhex("E5 A4 A9 E6 B0")  # 天 + first two bytes of 气


class _Backend:
    class ByteLevel:
        pass

    decoder = ByteLevel()


class FakeTokenizer:
    """ByteLevel tokenizer stand-in mapping each token ID to raw byte pieces."""

    backend_tokenizer = _Backend()
    all_special_ids = (SPECIAL_ID, STOP_ID)  # tuple keeps the class attribute immutable
    eos_token_id = EOS_ID
    pad_token_id = None

    def __init__(self, pieces):
        self.pieces = pieces

    def __call__(self, text, return_tensors="pt", truncation=False):
        return {"input_ids": torch.tensor([[SPECIAL_ID]])}

    def convert_ids_to_tokens(self, token_id):
        return "".join(BYTE_ENCODER[byte] for byte in self.pieces[token_id])

    def decode(self, token_ids, skip_special_tokens=False):
        if token_ids == [SPECIAL_ID]:
            return "<|im_start|>"
        if token_ids == [STOP_ID]:
            return "<|endoftext|>"
        if token_ids == [EOS_ID]:
            return "</s>"
        return self.pieces[token_ids[0]].decode("utf-8", errors="replace")


class ScriptedModel:
    """Emits the scripted token IDs in order by making one logit dominant."""

    def __init__(self, script):
        self.script = list(script)
        self.calls = 0

    def __call__(self, **kwargs):
        target = self.script[min(self.calls, len(self.script) - 1)]
        self.calls += 1
        vocab = max(self.script) + 1
        logits = torch.full((1, 1, vocab), -10.0)
        logits[0, 0, target] = 10.0
        return types.SimpleNamespace(logits=logits, past_key_values=None)


def run_generation(pieces, script, max_new_tokens):
    """Drive the real ``generate_with_streaming`` with a scripted model."""
    agent = types.SimpleNamespace(
        tokenizer=FakeTokenizer(pieces),
        model=ScriptedModel(script),
        device="cpu",
    )
    torch.manual_seed(0)
    text, _ = ReActAttentionAgent.generate_with_streaming(
        agent,
        prompt="prompt",
        max_new_tokens=max_new_tokens,
        temperature=1.0,
        verbose=False,
        track_attention=False,
    )
    return text


class EndOfStreamFlushTests(unittest.TestCase):
    """Generation ending on an incomplete character must not drop its bytes."""

    def test_max_new_tokens_exit_flushes_pending_bytes(self):
        text = run_generation({1: SPACE_AND_PARTIAL_TIAN}, [1], max_new_tokens=1)
        self.assertEqual(text, " \ufffd")

    def test_eos_exit_flushes_pending_bytes(self):
        text = run_generation({1: SPACE_AND_PARTIAL_TIAN}, [1, EOS_ID], max_new_tokens=5)
        self.assertEqual(text, " \ufffd")

    def test_rebuild_does_not_duplicate_the_last_token(self):
        # One token carrying a complete character plus the first bytes of the
        # next one. Rebuilding from generated_ids must give "天�"; appending the
        # final [-1] label to the streamed text would give "天天�".
        text = run_generation({1: TIAN_AND_PARTIAL_QI}, [1], max_new_tokens=1)
        self.assertEqual(text, "天\ufffd")

    def test_partial_character_is_not_flushed_early(self):
        # " " + 天 split across two tokens: no replacement character while the
        # character is still being completed, and no duplicated "天".
        text = run_generation(
            {1: SPACE_AND_PARTIAL_TIAN, 2: PARTIAL_TIAN}, [1, 2], max_new_tokens=2
        )
        self.assertEqual(text, " 天")
        self.assertNotIn("\ufffd", text)

    def test_stop_string_exit_keeps_text_before_the_stop_string(self):
        # "</s>" plus a partial character in the same final token: the stop
        # string ends generation and the pending bytes are cut with it.
        pieces = {1: BEIJING, 2: b"</s>" + bytes.fromhex("E5 A4")}
        text = run_generation(pieces, [1, 2], max_new_tokens=5)
        self.assertEqual(text, "北京")
        self.assertNotIn("\ufffd", text)

    def test_special_stop_token_keeps_text_flushed_before_it(self):
        # A partial UTF-8 character followed by a special stop token. Decoding
        # flushes "�" into the label before the special token, but the streamed
        # accumulation only appends the newest label, so generated_text never
        # sees it. The stop offset must come from the finalized text, otherwise
        # the flushed character is cut off and the result is empty.
        text = run_generation({1: INCOMPLETE_TIAN_PREFIX}, [1, STOP_ID], max_new_tokens=5)
        self.assertEqual(text, "\ufffd")

    def test_complete_generation_gets_no_spurious_replacement_character(self):
        text = run_generation(
            {1: BEIJING, 2: bytes.fromhex("20 E6 B0 94")}, [1, 2], max_new_tokens=2
        )
        self.assertEqual(text, "北京 气")
        self.assertNotIn("\ufffd", text)


if __name__ == "__main__":
    unittest.main()
