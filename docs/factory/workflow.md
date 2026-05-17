# Factory Workflow

## Functional states
- Backlog
- Ready for refinement
- Ready for architecture review
- Ready for implementation
- Ready for QA
- Ready for PO review
- Ready for human review
- Done
- Blocked

## Execution states
- idle
- running
- waiting_human
- failed

Functional state answers **what phase the ticket is in**.
Execution state answers **whether an agent currently owns or is waiting on the ticket**.

## Initial routing
- Ready for refinement -> Product Owner
- Ready for architecture review -> Architect
- Ready for implementation -> Implementation Engineer
- Ready for QA -> Quality + Security Gate
- Ready for PO review -> Product Owner
- Ready for human review -> Human
- Blocked -> wait / resolve blocker

## Legal transitions

| From | Allowed next states |
|---|---|
| Backlog | Ready for refinement, Blocked |
| Ready for refinement | Ready for architecture review, Ready for implementation, Blocked, Backlog |
| Ready for architecture review | Ready for implementation, Ready for refinement, Blocked |
| Ready for implementation | Ready for QA, Ready for architecture review, Ready for refinement, Blocked |
| Ready for QA | Ready for PO review, Ready for implementation, Blocked |
| Ready for PO review | Done, Ready for implementation, Ready for refinement, Blocked |
| Ready for human review | Done, Ready for implementation, Ready for refinement, Blocked |
| Blocked | Backlog, Ready for refinement, Ready for architecture review, Ready for implementation, Ready for QA, Ready for PO review, Ready for human review |
| Done | Ready for implementation, Ready for QA, Ready for PO review, Ready for human review, Blocked |

## Rework / rollback paths
- QA can send work back to implementation.
- PO or human review can reopen implementation/refinement.
- Done can be reopened for a controlled follow-up or rollback path.
- Blocked always requires a blocking reason.

## Dispatch rules
- Dispatch only considers tickets whose dependencies are all `Done`.
- Tickets in inconsistent states are rejected unless `--force` is used.
- Priority is respected before ticket ID ordering.
- `--max-tickets` controls how many actionable tickets may be claimed in one dispatch.
- `running` tickets are surfaced as potentially running/stale for manual review.

## Semi-auto default flow
1. Human or supervisor prepares / refines a ticket.
2. `factory dispatch --automation-mode semi-auto` claims actionable work.
3. `factory codex-prepare <TICKET_ID> <file>` creates a Codex task payload.
4. Codex returns structured JSON matching the output contract.
5. `factory apply-output <output.json>` validates the output, validates transition, updates canvas + markdown, and appends lightweight traceability.
6. Human reviews the result and dispatches the next ticket.
