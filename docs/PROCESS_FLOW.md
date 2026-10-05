# Resume–Job Matching Engine: process flows

## Domain request

Endpoint: `POST /match`. Stages summarize [src/jobmatch/match.py](../src/jobmatch/match.py). This is in-process Python, not a hosted model or production apply.

```mermaid
flowchart TD
  A["POST /match"] --> B{"Valid input?"}
  B -->|"No"| E["HTTP 422"]
  B -->|"Yes: Non-empty resume string"| C["Domain function in match.py"]
  C --> O["Jaccard ranks for two jobs"]
  O --> X["No production side effect"]
```

See [INTERVIEW_QA.md](../INTERVIEW_QA.md) for fixture walkthroughs and [PROJECT_ARCHITECTURE.md](../PROJECT_ARCHITECTURE.md) for the component map.
