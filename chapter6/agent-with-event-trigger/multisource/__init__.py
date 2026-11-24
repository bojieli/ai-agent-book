"""Experiment 6-1 extension: multi-source ingress with fault injection.

Three sources -- a local test mailbox, a signed Webhook endpoint and an SQS
queue -- feed one append-only ingress log. Each adapter verifies its source,
builds an envelope, writes it to the log, and only then acknowledges the
source. The runtime reads the log and handles events in per-thread order,
recording every reply in an outbox before it is sent.

Module map, in dependency order:

* ``envelope``  -- the unified event envelope (book, "接入层：多种来源，一种事件")
* ``store``     -- ingress log + audit trail, source progress, dispatch
                   progress, task state and outbox (one SQLite file)
* ``fake_sqs``  -- a file-backed SQS stand-in with visibility timeouts
* ``faults``    -- named fault points and the helper that kills a process there
* ``adapters``  -- Webhook (HTTP + HMAC), SQS poller and mailbox poller
* ``channels``  -- outbound channels: mail (Sent lookup), app chat
                   (idempotency key) and SMS (neither)
* ``runtime``   -- router, responder, outbox reconciliation and the event loop
"""
