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
import { user } from "./auth.schema";

export const document = pgTable(
  "document",
  {
    id: uuid("id").primaryKey(),
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
