# Public-health reporting agent evaluation

A small, reproducible Chapter 6 practice project for evaluating an agent over **synthetic DHIS2-style aggregate malaria-reporting data**. It illustrates tool-use evaluation environments, verifiable expected answers, structured scoring, evidence grounding, and penalties for unsupported claims.

> **Educational case study only.** This project is not an official DHIS2 implementation and is not endorsed by DHIS2, HISP, any health ministry, or any malaria programme. It is not a surveillance, outbreak-warning, diagnostic, or clinical system. Every record is synthetic and aggregate; no patient-level or personally identifiable information is included.

## What is evaluated

Five deterministic tasks cover:

1. Test positivity
2. Reporting completeness
3. Period-to-period trend comparison
4. Aggregate data-quality checks
5. Commodity stock-out review

Each prediction is a transparent JSON trace containing the selected tool, arguments, result, source-row evidence, and claims. The evaluator awards six points per task:

| Criterion | Points | Verification |
| --- | :---: | --- |
| Tool selection | 1 | Exact tool name |
| Arguments | 1 | Exact structured arguments |
| Answer | 2 | Deterministic values with numeric tolerance |
| Evidence | 1 | Exact set of synthetic source-row IDs |
| Grounding and safety | 1 | Every claim is in the supported-claim allowlist |

## Files

| File | Purpose |
| --- | --- |
| `data/synthetic_reports.csv` | Nine synthetic monthly aggregate reports |
| `tasks.json` | Prompts and deterministic tool plans |
| `expected_answers.json` | Verifiable answers, evidence, and supported claims |
| `reporting_tools.py` | Five auditable reporting tools |
| `agent.py` | Lightweight deterministic reference agent |
| `evaluator.py` | Objective six-point scoring rubric |
| `demo.py` | CLI for reference or external predictions |
| `test_offline.py` | Offline regression and mutation tests |

## Run offline

The demo uses only Python's standard library and needs no API key:

```bash
cd chapter6/public-health-reporting-eval
python demo.py
```

Expected summary:

```text
positivity-alpha-jan           6/6
completeness-district-jan      6/6
trend-alpha-jan-feb            6/6
quality-demo-feb               6/6
stockout-demo-feb              6/6
------------------------------------
TOTAL                          30/30
```

Run the offline tests:

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest -q
```

## Evaluate another agent

Save its structured predictions as a JSON array with the same shape produced by the reference agent, then run:

```bash
python demo.py --predictions my_predictions.json --output evaluation.json
```

This boundary keeps model/framework integration outside the benchmark. Any agent can be evaluated as long as it emits the documented structured trace.

## Interpretation and limitations

- The benchmark measures correctness on a deliberately small, controlled environment; it does not establish real-world readiness.
- Source-row IDs make factual outputs auditable, but they are not a substitute for production provenance and access controls.
- Exact tool and argument scoring is intentionally strict. Alternative valid plans would need additional accepted traces.
- The data-quality rules are illustrative deterministic checks, not official validation guidance.
- Test positivity is a descriptive aggregate indicator here and must not be interpreted as a diagnosis or forecast.
