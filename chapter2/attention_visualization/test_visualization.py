"""Regression tests for attention-heatmap axis labels.

``clean_token_labels`` turns raw tokenizer tokens into readable axis labels.
The case that matters here: a Qwen3 ByteLevel tokenizer splits a multi-byte
UTF-8 character across tokens, and ``decode_token_labels`` assigns the character
to the token that completes it, so the earlier tokens legitimately decode to
``""``. Those positions are continuations of a character, not spaces, and must
not be labelled with the space glyph.
"""

import unittest

import matplotlib.pyplot as plt
import numpy as np
from visualization import (
    clean_token_labels,
    create_attention_flow_diagram,
    create_attention_heatmap,
    create_layer_attention_heatmap,
)


class CleanTokenLabelsTests(unittest.TestCase):
    def test_continuation_token_is_not_rendered_as_a_space(self):
        self.assertEqual(clean_token_labels(["", " ", "天"]), ["↳", "␣", "天"])

    def test_continuation_and_space_labels_stay_distinct(self):
        cleaned = clean_token_labels(["", " "])
        self.assertEqual(cleaned[0], "↳")
        self.assertEqual(cleaned[1], "␣")
        self.assertNotEqual(cleaned[0], cleaned[1])

    def test_character_split_across_three_tokens_marks_every_continuation(self):
        self.assertEqual(clean_token_labels(["", "", "气"]), ["↳", "↳", "气"])

    def test_byte_level_space_markers_still_map_to_the_space_glyph(self):
        self.assertEqual(clean_token_labels([" ", "Ġ", "▁"]), ["␣", "␣", "␣"])

    def test_escaped_whitespace_is_not_mistaken_for_a_continuation(self):
        self.assertEqual(clean_token_labels(["\n", "\t"]), ["\\n", "\\t"])

    def test_long_labels_are_still_truncated(self):
        self.assertEqual(clean_token_labels(["x" * 20], max_len=5), ["xxxx…"])


class HeatmapMarkerRenderingTests(unittest.TestCase):
    """Marker ticks must render through the helper that fixes their font."""

    def test_continuation_and_space_markers_render_on_the_heatmap(self):
        matrix = np.asarray([[1.0, 0.0, 0.0], [0.5, 0.5, 0.0], [0.3, 0.3, 0.4]])
        fig = create_layer_attention_heatmap(matrix, ["", " ", "天"], title="markers")
        try:
            ticks = fig.axes[0].get_xticklabels()
            self.assertEqual([tick.get_text() for tick in ticks], ["↳", "␣", "天"])
            # The CJK font lacks U+2423/U+21B3, so the helper must switch fonts.
            self.assertEqual(ticks[0].get_fontfamily(), ["DejaVu Sans"])
            self.assertEqual(ticks[1].get_fontfamily(), ["DejaVu Sans"])
        finally:
            plt.close(fig)

    def test_legacy_heatmap_marks_continuations_on_both_axes(self):
        fig = create_attention_heatmap(
            [[0.2, 0.3, 0.5]], ["", "天"], [""], context_boundary=2
        )
        try:
            ax = fig.axes[0]
            self.assertEqual([tick.get_text() for tick in ax.get_xticklabels()], ["↳", "天", "↳"])
            self.assertEqual([tick.get_text() for tick in ax.get_yticklabels()], ["↳"])
            self.assertEqual(ax.images[0].get_array().shape, (1, 3))
        finally:
            plt.close(fig)

    def test_flow_step_title_marks_continuation(self):
        fig = create_attention_flow_diagram(
            [{"step": 1, "token": "", "attention_weights": [0.4, 0.6]}],
            ["天"], context_length=1,
        )
        try:
            self.assertIn("↳", fig.axes[0].get_title())
            self.assertEqual(fig.axes[0].title.get_fontfamily(), ["DejaVu Sans"])
        finally:
            plt.close(fig)


if __name__ == "__main__":
    unittest.main()
