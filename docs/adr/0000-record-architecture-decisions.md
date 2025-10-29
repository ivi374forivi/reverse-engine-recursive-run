# Architecture Decision Records (Index)

This directory contains Architecture Decision Records (ADRs) that document significant architectural choices made during the development and evolution of this system.

| Number | Title | Status | Date | File |
|--------|-------|--------|------|------|
| 0000 | Record Architecture Decisions | Accepted | 2025-10-29 | [0000-record-architecture-decisions.md](0000-record-architecture-decisions.md) |

Legend: Status values = Proposed | Accepted | Deprecated | Superseded

## About ADRs

An Architecture Decision Record (ADR) is a document that captures an important architectural decision made along with its context and consequences.

### When to Create an ADR

- Significant architectural changes
- New boundary violations detected by drift analysis
- Major security decisions
- Technology stack changes
- Process changes affecting architecture

### ADR Workflow

1. Detect trigger (drift breach, high-risk hotspot, security mandate)
2. Run `./scripts/adr_new.sh "Decision Title"`
3. Fill in the template sections
4. Submit for PR review
5. Status changes: Proposed → Accepted (after approval)
6. Update index automatically via `python scripts/adr_index.py`

## Quality Checklist

- Context references objective evidence (risk report SHA)
- Decision unambiguously states chosen direction
- Alternatives list at least two meaningful options
- Consequences include risks & follow-up tasks
- Implementation plan identifies owners & rollback triggers

Generated: 2025-10-29
