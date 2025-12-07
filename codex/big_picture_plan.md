<!--
codex/big_picture_plan.md
High-level migration roadmap for moving the Django template app to a Next.js frontend backed by DRF.
This file exists to guide the team through staged delivery, track migration progress, and serve as a checklist for porting features.
-->

# Next.js + DRF Migration Big Picture Plan

## Goals & Guardrails
- Maintain feature parity with the existing Django templates, starting with samples and user management.
- Deliver a DRF API that mirrors current behavior so the Next.js frontend can slot in without business logic rewrites.
- Preserve JWT-based authentication flows and avoid database schema changes unless explicitly approved later.
- Keep the Django app stable during migration; enable incremental rollout without user disruption.

## Guiding Principles
- Mirror before you improve: replicate functionality first, then iterate on UX.
- Favor small, vertical slices that move a feature end-to-end (DRF endpoint, Next.js UI, integration tests).
- Reuse existing domain and data models from Django; add DRF serializers/viewsets around them.
- Share validation/business rules between backend and frontend where possible to prevent regressions.
- Document API contracts as they are solidified to help with future Next.js iterations.

## Implementation Checklist & Status
- [x] Auth: DRF + Next.js login/logout flow mirrors existing JWT behavior.
- [x] Samples: Main dashboard sample fetching powered by DRF endpoint and consumed by Next.js table.
- [ ] Auth: Registration, password reset, and profile update endpoints with Next.js pages.
- [ ] Samples: Sample detail, edit, and media handling parity with legacy app.
- [ ] Infrastructure: Observability, CI alignment, and deployment pipelines for the dual-stack rollout.
- [ ] Feature flag/rollout strategy defined for gradual cutover.

## Phase 1 — Foundations (Weeks 1-4)
- **Project setup**: Harden Next.js repo (linting, type-checking, testing), align with existing CI.
- **DRF scaffolding**: Add DRF to Django project, configure routing, permissions, versioning, JWT auth integration.
- **Shared auth utilities**: Create reusable auth client for Next.js calling DRF; ensure token refresh flow matches current behavior.
- **Observability**: Establish logging, error tracking, and API monitoring baselines for new stack components.

## Phase 2 — Samples Feature Slice (Weeks 5-12)
- **API parity**: Expose DRF endpoints for listing, searching, viewing, and editing samples mirroring current views. *(Listing endpoint powering the main dashboard table is complete.)*
- **Data contracts**: Define serializers and response schemas; backfill automated tests against existing sample behavior.
- **Next.js UI**: Build samples listing/detail flows; ensure routing, pagination, and filtering match current UX.
- **File/media handling**: Confirm media delivery strategy (direct links, signed URLs); document any deviations.
- **Cutover checkpoint**: Run side-by-side validation (Django templates vs. Next.js) and gate switchover with QA signoff.

## Phase 3 — User Management & Auth UX (Weeks 13-18)
- **Account endpoints**: Implement DRF endpoints for registration, profile management, password reset, and roles/permissions.
- **Session handling**: Wire Next.js pages for login/logout, multi-factor (if applicable), and account recovery. *(Login/logout completed; ensure token refresh stays aligned.)*
- **Access control**: Mirror current user role restrictions in DRF permissions and propagate to frontend guards.
- **Compliance**: Audit password policies, email flows, and terms/privacy acknowledgements; port templates as needed.

## Phase 4 — Remaining Features & Content (Weeks 19-22)
- **Inventory migration**: Prioritize remaining Django template flows (e.g., dashboards, analytics, admin tooling); tackle in feature batches.
- **Reusable components**: Abstract shared UI/state patterns discovered in earlier phases for reuse.
- **API expansion**: Continue exposing DRF endpoints feature-by-feature, maintaining parity with legacy behavior.

## Phase 5 — Stabilization & Handover (Weeks 23-26)
- **Regression testing**: Build comprehensive automated and manual regression passes comparing old vs. new.
- **Performance hardening**: Profile API/Next.js performance; optimize hot paths and bundle sizes.
- **Rollout plan**: Define deployment strategy (beta cohorts, feature flags, rollback).
- **Documentation**: Finalize developer docs, API specs, and runbooks for operating the new stack.

## Cross-Cutting Checklist
- Maintain synchronized environments (dev/staging/prod) for Django+DRF and Next.js.
- Keep a running parity matrix tracking which legacy features are ported, pending, or deprecated.
- Align stakeholder demos with each phase milestone for feedback and course correction.
- Plan for knowledge transfer and training sessions once new stack stabilizes.

## Open Questions
- Do we need feature flags to toggle between Django templates and Next.js pages per route?
- What QA resources and cadence will support each cutover checkpoint?
- Are there content updates that should ship alongside new UX during the migration?
