"""Regression tests for labels when UTF-8 characters cross token boundaries."""

import unittest

from token_labels import BYTE_DECODER, decode_token_labels


BYTE_ENCODER = {byte: char for char, byte in BYTE_DECODER.items()}


class ByteLevelTokenizer:
    class Backend:
        class ByteLevel:
            pass

        decoder = ByteLevel()

    backend_tokenizer = Backend()
    all_special_ids = [0]

    def __init__(self, pieces):
        self.pieces = pieces

    def convert_ids_to_tokens(self, token_id):
        return "".join(BYTE_ENCODER[byte] for byte in self.pieces[token_id])

    def decode(self, token_ids, skip_special_tokens=False):
        if token_ids == [0]:
            return "<|im_start|>"
        return self.pieces[token_ids[0]].decode("utf-8", errors="replace")


class TokenLabelTests(unittest.TestCase):
    def test_qwen_split_characters_keep_nine_positions(self):
        pieces = {
            68990: bytes.fromhex("E5 8C 97 E4 BA AC"),
            43589: bytes.fromhex("20 E7 9A 84"),
            40666: bytes.fromhex("20 E5 A4"),
            102: bytes.fromhex("A9"),
            99180: bytes.fromhex("E6 B0 94"),
            90476: bytes.fromhex("20 E6 80"),
            236: bytes.fromhex("8E"),
            81596: bytes.fromhex("E4 B9 88"),
            90885: bytes.fromhex("E6 A0 B7"),
        }
        ids = list(pieces)
        labels = decode_token_labels(ByteLevelTokenizer(pieces), ids)
        self.assertEqual(labels, ["北京", " 的", " ", "天", "气", " ", "怎", "么", "样"])
        self.assertEqual("".join(labels), "北京 的 天气 怎么样")

    def test_special_tokens_end_pending_bytes(self):
        tokenizer = ByteLevelTokenizer({1: b"\xe5\xa4", 2: b"\xa9"})
        self.assertEqual(
            decode_token_labels(tokenizer, [0, 1, 2, 0]),
            ["<|im_start|>", "", "天", "<|im_start|>"],
        )
        self.assertEqual(
            decode_token_labels(tokenizer, [1, 0, 2]),
            ["�", "<|im_start|>", "�"],
        )

    def test_other_tokenizer_uses_regular_decode(self):
        class PlainTokenizer:
            def decode(self, ids, skip_special_tokens=False):
                return str(ids[0])

        self.assertEqual(decode_token_labels(PlainTokenizer(), [1, 2]), ["1", "2"])
        self.assertEqual(
            decode_token_labels(PlainTokenizer(), [1, 2], final=False), ["1", "2"]
        )


class PrefixDecodeTests(unittest.TestCase):
    """A growing generation prefix must not flush incomplete UTF-8 bytes."""

    def test_incomplete_prefix_has_no_replacement_char(self):
        tokenizer = ByteLevelTokenizer({1: b"\xe5\xa4", 2: b"\xa9"})
        self.assertEqual(decode_token_labels(tokenizer, [1], final=False), [""])
        self.assertNotIn("\ufffd", "".join(decode_token_labels(tokenizer, [1], final=False)))

    def test_completed_prefix_assigns_char_to_final_token(self):
        tokenizer = ByteLevelTokenizer({1: b"\xe5\xa4", 2: b"\xa9"})
        labels = decode_token_labels(tokenizer, [1, 2], final=False)
        self.assertEqual(labels, ["", "天"])
        self.assertEqual(len(labels), 2)

    def test_prefix_keeps_complete_text_before_incomplete_char(self):
        tokenizer = ByteLevelTokenizer({1: b" \xe5\xa4", 2: b"\xa9"})
        self.assertEqual(decode_token_labels(tokenizer, [1], final=False), [" "])
        self.assertEqual(decode_token_labels(tokenizer, [1, 2], final=False), [" ", "天"])

    def test_one_label_per_token_is_preserved(self):
        tokenizer = ByteLevelTokenizer({1: b"\xe5\xa4", 2: b"\xa9", 3: b"\xe6\xb0"})
        for length in (1, 2, 3):
            ids = [1, 2, 3][:length]
            self.assertEqual(len(decode_token_labels(tokenizer, ids, final=False)), length)

    def test_final_true_still_flushes_truncated_sequence(self):
        tokenizer = ByteLevelTokenizer({1: b"\xe5\xa4", 2: b"\xa9"})
        self.assertEqual(decode_token_labels(tokenizer, [1], final=True), ["\ufffd"])
        # ``final`` defaults to True, so existing complete-sequence callers do
        # not change behavior.
        self.assertEqual(decode_token_labels(tokenizer, [1]), ["\ufffd"])

        spaced = ByteLevelTokenizer({1: b" \xe5\xa4"})
        self.assertEqual(decode_token_labels(spaced, [1]), [" \ufffd"])

    def test_complete_sequence_same_for_both_modes(self):
        pieces = {
            68990: bytes.fromhex("E5 8C 97 E4 BA AC"),
            43589: bytes.fromhex("20 E7 9A 84"),
            40666: bytes.fromhex("20 E5 A4"),
            102: bytes.fromhex("A9"),
            99180: bytes.fromhex("E6 B0 94"),
            90476: bytes.fromhex("20 E6 80"),
            236: bytes.fromhex("8E"),
            81596: bytes.fromhex("E4 B9 88"),
            90885: bytes.fromhex("E6 A0 B7"),
        }
        ids = list(pieces)
        expected = ["北京", " 的", " ", "天", "气", " ", "怎", "么", "样"]
        tokenizer = ByteLevelTokenizer(pieces)
        self.assertEqual(decode_token_labels(tokenizer, ids, final=False), expected)
        self.assertEqual(decode_token_labels(tokenizer, ids, final=True), expected)
        self.assertEqual(len(expected), 9)
        self.assertEqual("".join(expected), "北京 的 天气 怎么样")

    def test_streaming_accumulation_never_appends_replacement_char(self):
        """Mirror the streaming loops in main.py/agent.py: append the newest label."""
        tokenizer = ByteLevelTokenizer(
            {
                1: b"\xe5\xa4",
                2: b"\xa9",
                3: bytes.fromhex("E6 B0 94"),
                4: bytes.fromhex("20 E6 A0"),
                5: b"\xb7",
            }
        )
        generated_ids = []
        generated_text = ""
        streamed_tokens = []
        for token_id in (1, 2, 3, 4, 5):
            generated_ids.append(token_id)
            token_text = decode_token_labels(tokenizer, generated_ids, final=False)[-1]
            streamed_tokens.append(token_text)
            generated_text += token_text

        # No intermediate step may leak a replacement character.
        self.assertNotIn("\ufffd", generated_text)
        self.assertNotIn("\ufffd", "".join(streamed_tokens))
        self.assertEqual(streamed_tokens, ["", "天", "气", " ", "样"])
        self.assertEqual(generated_text, "天气 样")
        # The accumulated stream matches a single complete-sequence decode.
        self.assertEqual(
            generated_text,
            "".join(decode_token_labels(tokenizer, generated_ids, final=True)),
        )


if __name__ == "__main__":
    unittest.main()
