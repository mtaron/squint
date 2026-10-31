import {
  bigint,
  boolean,
  index,
  integer,
  pgTable,
  primaryKey,
  real,
  text,
  timestamp,
  unique,
  uuid,
} from "drizzle-orm/pg-core";
import { user } from "./auth.schema";

export const document = pgTable(
  "document",
  {
    id: text("id").primaryKey(),
    userId: uuid("user_id")
      .notNull()
      .references(() => user.id, { onDelete: "cascade" }),
    name: text("name").notNull(),
    sha256: text("sha256").notNull(),
    sizeBytes: bigint("size_bytes", { mode: "number" }).notNull(),
    pageCount: integer("page_count"),
    uploadedAt: timestamp("uploaded_at", { withTimezone: true }).defaultNow().notNull(),
  },
  (table) => [
    unique("document_user_sha256_unique").on(table.userId, table.sha256),
    index("document_user_uploaded_idx").on(table.userId, table.uploadedAt),
  ],
);

/** What ingestion learned about each page. Pixel values are relative to the page's image in S3. */
export const documentPage = pgTable(
  "document_page",
  {
    documentId: text("document_id")
      .notNull()
      .references(() => document.id, { onDelete: "cascade" }),
    pageNumber: integer("page_number").notNull(),
    width: integer("width").notNull(),
    height: integer("height").notNull(),
    isScan: boolean("is_scan").notNull(),
    /** The rotation applied to straighten a scan, or null if the image is as rendered. */
    skewDegrees: real("skew_degrees"),
    /** [left, top, right, bottom] around the page's ink, or null if the page is blank. */
    contentBox: integer("content_box").array(),
  },
  (table) => [primaryKey({ columns: [table.documentId, table.pageNumber] })],
);
