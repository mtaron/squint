-- Hand-edited: existing documents have no page images and use the old object key layout, so they are deleted.
DELETE FROM "document";--> statement-breakpoint
CREATE TABLE "document_page" (
	"document_id" text NOT NULL,
	"page_number" integer NOT NULL,
	"width" integer NOT NULL,
	"height" integer NOT NULL,
	"is_scan" boolean NOT NULL,
	"skew_degrees" real,
	"content_box" integer[],
	CONSTRAINT "document_page_document_id_page_number_pk" PRIMARY KEY("document_id","page_number")
);
--> statement-breakpoint
ALTER TABLE "document_page" ADD CONSTRAINT "document_page_document_id_document_id_fk" FOREIGN KEY ("document_id") REFERENCES "public"."document"("id") ON DELETE cascade ON UPDATE no action;