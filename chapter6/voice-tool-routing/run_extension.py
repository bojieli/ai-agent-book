#!/usr/bin/env python3
"""Extension scenarios, run with the same runtime as run_experiment.py.

``booking_dictated``: like ``booking``, but the passenger is a (fictional) colleague whose name,
passport number and phone number are dictated by voice in the second turn.  In the delegated
routes the back LLM only sees the speech-recognition transcript of that dictation, whereas the
front model hears the audio itself; this makes the "just heard" booking fields high-entropy.

It lives in its own file so that run_experiment.py stays byte-identical to the version that
produced the main run.
"""

from __future__ import annotations

import sys

import run_experiment

run_experiment.SCENARIOS["booking_dictated"] = [
    ("say", "flight_search", 0),
    ("say", "booking_dictated", 0),
    ("say", "booking_confirm", 0),
]

if __name__ == "__main__":
    if "--scenarios" not in sys.argv:
        sys.argv += ["--scenarios", "booking_dictated"]
    sys.exit(run_experiment.main())
