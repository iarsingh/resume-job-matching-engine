# resume-job-matching-engine — interview questions and answers

[README](README.md) · [Project architecture](PROJECT_ARCHITECTURE.md)

Answers below use this repository’s files and implementation. They distinguish existing behavior from suggested extensions; source links let you verify each walkthrough.

## 1. What problem does resume-job-matching-engine address, and what can you demonstrate?

Rank a small job catalog by token overlap with a resume. Empty resumes are refused.

I would demonstrate the linked implementation or examples and distinguish that evidence from any planned production features. Start with [`README.md`](README.md).

## 2. How is this repository organized?

- [`src/jobmatch/main.py`](src/jobmatch/main.py): Implementation or supporting configuration.
- [`src/jobmatch/match.py`](src/jobmatch/match.py): Implementation or supporting configuration.
- [`requirements.txt`](requirements.txt): Implementation or supporting configuration.
- [`src/jobmatch/__init__.py`](src/jobmatch/__init__.py): Implementation or supporting configuration.
- [`tests/test_match.py`](tests/test_match.py): Executable checks and regression examples.
- [`.github/workflows/ci.yml`](.github/workflows/ci.yml): GitHub Actions job definitions.
- [`README.md`](README.md): Project explanations or operating notes.

[PROJECT_ARCHITECTURE.md](PROJECT_ARCHITECTURE.md) contains the component diagram and the implementation walkthrough.

## 3. Can you walk through `match` and explain the decision it makes?

The main walkthrough here is `match(resume)` in [`src/jobmatch/match.py`](src/jobmatch/match.py#L10).

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

The implementation calls `JOBS.items`, `ValueError`, `isinstance`, `len`, `ranked.append`, `ranked.sort`, `resume.strip`, `round`, `tokens`. In an interview, trace those calls in execution order using a fixture input.

## 4. What responsibility does `tokens` have?

`tokens(text)` is defined in [`src/jobmatch/match.py`](src/jobmatch/match.py#L6).

Its return expressions include:

- `set(re.findall('[a-z0-9]+', text.lower()))`

It uses `re.findall`, `set`, `text.lower`. This is the code path I would compare against the caller to explain responsibility boundaries.

## 5. What input validation and failure behavior are implemented?

Explicit failure paths include:

- `HTTPException(status_code=422, detail=str(exc))` in [`src/jobmatch/main.py`](src/jobmatch/main.py#L17).
- `ValueError('resume is empty')` in [`src/jobmatch/match.py`](src/jobmatch/match.py#L12).

I would test both the condition that reaches each exception and the caller that translates it. An explicit raise does not mean every malformed input or dependency failure is handled.

## 6. Which test would you use to demonstrate correctness?

[`tests/test_match.py`](tests/test_match.py#L7) contains `test_ranks_the_closest_job`:

```python
def test_ranks_the_closest_job():
    payload = client.post("/match", json={"resume": 'kubernetes terraform oncall sre'}).json()
    assert payload["matches"][0]["job"] == "platform"
```

This is a concrete regression example from the repository. Its assertions establish that case; they do not establish behavior for every input or under production load.

## 7. What HTTP interface does the code expose?

- `GET /healthz` → `healthz` in [`src/jobmatch/main.py`](src/jobmatch/main.py#L8).
- `POST /match` → `post_match` in [`src/jobmatch/main.py`](src/jobmatch/main.py#L13).

These are literal decorators. Application/router prefixes, authentication, and middleware must be checked in the corresponding setup code.

## 8. Where does state live, and what happens with multiple workers?

Module-level containers include `JOBS` in [`src/jobmatch/match.py`](src/jobmatch/match.py).

These containers belong to a Python process. Inspect which are constant fixtures and which are mutated. Mutable process state needs an explicit shared-storage or synchronization strategy before multiple workers can provide consistent behavior.

## 9. How would another engineer reproduce your walkthrough?

Start from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
```

These commands follow repository manifests; environment setup and command results still need to be checked on the target machine.

## 10. What does automation verify, and what does it not prove?

Inspect [`.github/workflows/ci.yml`](.github/workflows/ci.yml) for triggers, permissions, and job commands. I would name the checks that those definitions run and show the latest run separately. A workflow definition alone does not establish a successful deployment, security review, or production SLO.

## 11. How would you present this project in a Forward Deployed Engineer interview?

Start with the user and operational problem described in [`README.md`](README.md). Explain one constraint that changes the implementation, show the linked code or example, and walk through a success case and a failure case. Agree on a measurable acceptance criterion before expanding the solution, and leave a handoff with data boundaries and rollback ownership. Any proposed production or business metric should be identified as a target until measured.

## 12. What is the input-to-output contract of `match`?

In [`src/jobmatch/match.py`](src/jobmatch/match.py#L10), `match(resume)` receives the inputs. The function computes these intermediate values:

- `left = tokens(resume)`
- `ranked = []`

Its result is defined by:

- `{'matches': ranked}`

## 13. Which decision rules or boundary conditions should an interviewer challenge?

The implementation in [`src/jobmatch/match.py`](src/jobmatch/match.py#L10) branches on:

- `not isinstance(resume, str) or not resume.strip()`

A useful extension is a table-driven test that covers each condition just below, at, and above its boundary where applicable. These expressions are the current rules; changing them changes behavior and should be justified by the project’s acceptance criteria.
