# resume-job-matching-engine — project architecture

[README](README.md) · [Interview questions and answers](INTERVIEW_QA.md)

## Purpose and scope

Rank a small job catalog by token overlap with a resume. Empty resumes are refused.

This document describes files and symbols in this checkout. Deployment templates and statements in the original overview are distinguished from a verified running environment.

## Component diagram

```mermaid
flowchart LR
    M0["src/jobmatch/__init__.py"]
    M1["src/jobmatch/main.py"]
    M2["src/jobmatch/match.py"]
    M1 -->|imports| M2
```

For Python repositories, arrows show resolved local imports, not network calls or deployment order. Otherwise the diagram is a repository component map; containment arrows do not assert runtime integration.

## Components and responsibilities

| Component | Responsibility |
| --- | --- |
| [`src/jobmatch/main.py`](src/jobmatch/main.py) | HTTP handlers: `GET /healthz`, `POST /match` |
| [`src/jobmatch/match.py`](src/jobmatch/match.py) | Functions: `tokens`, `match` |
| [`requirements.txt`](requirements.txt) | Implementation or supporting configuration |
| [`src/jobmatch/__init__.py`](src/jobmatch/__init__.py) | Implementation or supporting configuration |
| [`tests/test_match.py`](tests/test_match.py) | Executable checks and regression examples |
| [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | GitHub Actions job definitions |
| [`README.md`](README.md) | Project explanations or operating notes |

## Request interface

| Method and path | Handler | Source |
| --- | --- | --- |
| `GET /healthz` | `healthz` | [`src/jobmatch/main.py`](src/jobmatch/main.py#L8) |
| `POST /match` | `post_match` | [`src/jobmatch/main.py`](src/jobmatch/main.py#L13) |

The table lists literal route decorators found in the inspected Python modules. Router prefixes and middleware can add behavior; check the linked handler and application setup before calling an endpoint.

## Implementation walkthrough

### `match(resume)`

Source: [`src/jobmatch/match.py`](src/jobmatch/match.py#L10).

Calls visible in this function: `JOBS.items`, `ValueError`, `isinstance`, `len`, `ranked.append`, `ranked.sort`, `resume.strip`, `round`, `tokens`.

```python
def match(resume):
    if not isinstance(resume, str) or not resume.strip():
        raise ValueError("resume is empty")
    left = tokens(resume)
    ranked = []
    for name, text in JOBS.items():
        right = tokens(text)
        score = len(left & right) / len(left | right) if left | right else 0
        ranked.append({"job": name, "score": round(score, 4)})
    ranked.sort(key=lambda row: -row["score"])
    return {"matches": ranked}
```

### `tokens(text)`

Source: [`src/jobmatch/match.py`](src/jobmatch/match.py#L6).

Calls visible in this function: `re.findall`, `set`, `text.lower`.

```python
def tokens(text):
    return set(re.findall(r"[a-z0-9]+", text.lower()))
```

## Validation and failure paths

| Explicit exception | Source |
| --- | --- |
| `HTTPException(status_code=422, detail=str(exc))` | [`src/jobmatch/main.py`](src/jobmatch/main.py#L17) |
| `ValueError('resume is empty')` | [`src/jobmatch/match.py`](src/jobmatch/match.py#L12) |

These are explicit exceptions in the inspected source, rather than a claim that every failure is handled. Follow the calling handler to see whether the exception becomes an HTTP response or propagates.

## Data and state

- [`src/jobmatch/match.py`](src/jobmatch/match.py) defines module-level containers: `JOBS`.

Module-level dictionaries/lists live in a Python process. They can be fixtures or mutable state; inspect writes before treating them as persistent storage. A production extension would need to define persistence and concurrency behavior explicitly.

## Data flow and design decisions

### What is the input-to-output contract of `match`

In [`src/jobmatch/match.py`](src/jobmatch/match.py#L10), `match(resume)` receives the inputs. The function computes these intermediate values:

- `left = tokens(resume)`
- `ranked = []`

Its result is defined by:

- `{'matches': ranked}`

### Which decision rules or boundary conditions should an interviewer challenge

The implementation in [`src/jobmatch/match.py`](src/jobmatch/match.py#L10) branches on:

- `not isinstance(resume, str) or not resume.strip()`

A useful extension is a table-driven test that covers each condition just below, at, and above its boundary where applicable. These expressions are the current rules; changing them changes behavior and should be justified by the project’s acceptance criteria.

## Setup and verification

The following commands are derived from the checked-in dependency/test contracts. Execute them from the repository root; the block prepares a local environment, not a cloud deployment.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
```

Python dependencies: [`requirements.txt`](requirements.txt).

Test entry points: [`tests/test_match.py`](tests/test_match.py).

Automation definitions: [`.github/workflows/ci.yml`](.github/workflows/ci.yml). Read their triggers and job steps to determine what CI actually runs.

## Operating boundaries and design review

Before turning this checkout into a customer deployment, establish the input contract, data ownership, access controls, failure response, evaluation criteria, and rollback owner. Repository fixtures and unit tests demonstrate local behavior; they do not establish throughput, uptime, compliance, or business impact.

A useful architecture review starts with the linked implementation: identify where input enters, where a decision is made, which state can change, and which external dependency can fail. Add a deployment view only for infrastructure that is actually configured and exercised.
