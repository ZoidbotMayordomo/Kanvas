# Workflow Factory

## Estados funcionales
- Backlog
- Ready for refinement
- Ready for architecture review
- Ready for implementation
- Ready for QA
- Ready for PO review
- Ready for human review
- Done
- Blocked

## Estado de ejecución
- idle
- running
- waiting_human
- failed

## Routing inicial
- Ready for refinement -> Product Owner
- Ready for architecture review -> Architect
- Ready for implementation -> Implementation Engineer
- Ready for QA -> Quality + Security Gate
- Ready for PO review -> Product Owner
- Ready for human review -> Human
- Blocked -> Reevaluate/Wait

## Regla importante
El estado funcional del ticket y el estado de ejecución son cosas distintas y no deben mezclarse.
