"""Small evaluation metrics helpers (no model deps)."""


def parse_rate(predicted: int, total: int) -> float:
    """Fraction of samples with a parseable prediction; empty total -> 0.0."""
    return predicted / total if total > 0 else 0.0
