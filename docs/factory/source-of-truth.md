# Source of Truth Policy

## Adopted decision
Hybrid model by field:
- **Canvas is authoritative** for visible and operational state.
- **Markdown is authoritative** for narrative detail and long-form traceability.

## Canvas-authoritative fields
- ticket title
- functional state
- execution state
- current role
- priority
- linked doc path
- dependencies
- blocking reason

These fields sync into `tickets/*.md` via `factory sync --write` and also during dispatch/apply-output.

## Markdown-authoritative sections
- Description
- Acceptance Criteria
- Dependencies narrative
- Relevant Context
- Decisions
- Implementation
- QA / Security
- Transition History
- Next Expected Step

## Operational implications
- `dispatch` may claim tickets by switching execution state to `running` in canvas and mirroring that change into markdown.
- `sync --write` corrects canvas-governed metadata in markdown without overwriting narrative sections.
- `apply-output` consumes validated structured agent output, updates the authoritative canvas fields, and appends minimal markdown traceability.
