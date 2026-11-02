export interface UploadDay<T> {
  /** The day as YYYY-MM-DD */
  key: string;
  label: string;
  documents: T[];
}

function dayKey(date: Date, timeZone: string): string {
  // The en-CA locale writes dates as YYYY-MM-DD
  return new Intl.DateTimeFormat("en-CA", { timeZone, dateStyle: "short" }).format(date);
}

function previousDay(key: string): string {
  const day = new Date(`${key}T00:00:00Z`);
  day.setUTCDate(day.getUTCDate() - 1);
  return day.toISOString().slice(0, 10);
}

function dayLabel(key: string, today: string, locale: string): string {
  if (key === today) {
    return "Today";
  }
  if (key === previousDay(today)) {
    return "Yesterday";
  }
  const sameYear = key.slice(0, 4) === today.slice(0, 4);
  return new Intl.DateTimeFormat(locale, {
    timeZone: "UTC",
    month: "long",
    day: "numeric",
    year: sameYear ? undefined : "numeric",
  }).format(new Date(`${key}T00:00:00Z`));
}

/** Splits documents, already in upload order, into the days they were uploaded on. */
export function groupByUploadDay<T extends { uploadedAt: Date }>(
  documents: T[],
  { timeZone, now, locale }: { timeZone: string; now: Date; locale: string },
): UploadDay<T>[] {
  const today = dayKey(now, timeZone);
  const days = new Map<string, UploadDay<T>>();
  for (const document of documents) {
    const key = dayKey(document.uploadedAt, timeZone);
    const day = days.get(key);
    if (day) {
      day.documents.push(document);
    } else {
      days.set(key, { key, label: dayLabel(key, today, locale), documents: [document] });
    }
  }
  return [...days.values()];
}

export function uploadedAtLabel(
  uploadedAt: Date,
  { timeZone, locale }: { timeZone: string; locale: string },
): string {
  const formatted = new Intl.DateTimeFormat(locale, {
    timeZone,
    dateStyle: "long",
    timeStyle: "short",
  }).format(uploadedAt);
  return `Uploaded ${formatted}`;
}
