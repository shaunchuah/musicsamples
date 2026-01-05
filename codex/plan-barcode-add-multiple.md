<!--
File: codex/plan-barcode-add-multiple.md
Description: Plan for recreating the legacy barcode add-multiple flow in the Next.js frontend.
Purpose: Capture agreed implementation steps before code changes, per project workflow.
-->

# Barcode Add-Multiple Plan

## Goal
Replicate the legacy `/barcode/add_multiple/` QR scan workflow in the Next.js frontend at
`/samples/qr-scan/add-multiple`, excluding the haemolysis reference palette image but keeping the
haemolysis field.

## Proposed Steps
1. Inventory legacy behavior (form fields, show/hide rules, scan submit, history table, alerts) and map them to Next.js UI components.
2. Add a Next.js page at `/samples/qr-scan/add-multiple` with the same input fields and scan area,
   minus the haemolysis palette image, and implement show/hide logic.
3. Add Next.js API routes that proxy to `api_v3` endpoints for:
   - POST `/api/multiple_samples/` (bulk add)
   - GET autocomplete for location, sublocation, and study ID
   Use the auth cookie for backend authorization.
4. Implement client-side scan handling (enter/tab submit), success/error alerts, scan history
   rendering, and autocomplete interactions; keep default timestamps aligned with legacy behavior.
5. Validate with manual smoke check (no server run unless requested) and document any gaps or open
   questions.
