// codex/plan-samples-search.md
// Plan for adding samples search UI and backend search endpoint.
// Exists to capture the implementation plan for future reference.

Plan:
1) Add a search action to the api_v3 samples endpoint that supports the legacy search fields, ordering, and pagination.
2) Add a Next.js dashboard proxy route for the new search API.
3) Update the SamplesTable to include a debounced search input and include-used checkbox, falling back to the list view when empty.
