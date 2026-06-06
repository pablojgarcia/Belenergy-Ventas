# OpenSpec Workflow

## Baseline Documentation

Located in:

- docs/vision.md
- docs/current-state.md
- docs/architecture.md
- docs/roadmap.md

## Active Changes

Located in:

- openspec/changes/

## Workflow

1. **Propose**: Create a new directory under `openspec/changes/` with `proposal.md` (include business goal, non-goals, assumptions) and `design.md` (include architecture impact, security considerations).
2. **Plan**: Create `tasks.md` with tasks smaller than one day of work.
3. **Apply**: Use `openspec-apply-change` to execute tasks.
4. **Archive**: Use `openspec-archive-change` to move the completed change directory to `openspec/changes/archive/`.
