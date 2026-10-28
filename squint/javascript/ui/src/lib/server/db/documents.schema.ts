import {
  bigint,
  index,
  integer,
  pgTable,
  text,
  timestamp,
  unique,
  uuid,
} from "drizzle-orm/pg-core";
import { documentStatuses, ingestErrors } from "#lib/uploads/documents.ts";
import { user } from "./auth.schema";

export const document = pgTable(
  "document",
  {
    id: uuid("id").primaryKey(),
    userId: text("user_id")
      .notNull()
      .references(() => user.id, { onDelete: "cascade" }),
    name: text("name").notNull(),
    sha256: text("sha256").notNull(),
    // Changes when the file is replaced, so a stale ingestion can't overwrite the new result
    uploadId: uuid("upload_id").notNull(),
    objectKey: text("object_key").notNull(),
    sizeBytes: bigint("size_bytes", { mode: "number" }).notNull(),
    status: text("status", { enum: documentStatuses }).notNull(),
    pageCount: integer("page_count"),
    errorCode: text("error_code", { enum: ingestErrors }),
    errorDetail: text("error_detail"),
    uploadedAt: timestamp("uploaded_at", { withTimezone: true }).defaultNow().notNull(),
    updatedAt: timestamp("updated_at", { withTimezone: true })
      .defaultNow()
      .$onUpdate(() => new Date())
      .notNull(),
  },
  (table) => [
    unique("document_user_sha256_unique").on(table.userId, table.sha256),
    index("document_user_uploaded_idx").on(table.userId, table.uploadedAt),
  ],
);

export type Document = typeof document.$inferSelect;
