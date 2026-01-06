// frontend/lib/formatters.ts
// Shared date/time formatter instances for dashboard tables and UI copy.
// Exists to keep date and time rendering consistent across samples, boxes, and experiments views.

export const dateFormatter = new Intl.DateTimeFormat("en-GB", {
  year: "numeric",
  month: "2-digit",
  day: "2-digit",
});

export const timeFormatter = new Intl.DateTimeFormat("en-GB", {
  hour: "2-digit",
  minute: "2-digit",
});
