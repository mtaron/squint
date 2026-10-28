CREATE TABLE "document" (
	"id" uuid PRIMARY KEY NOT NULL,
	"user_id" text NOT NULL,
	"name" text NOT NULL,
	"sha256" text NOT NULL,
	"upload_id" uuid NOT NULL,
	"object_key" text NOT NULL,
	"size_bytes" bigint NOT NULL,
	"status" text NOT NULL,
	"page_count" integer,
	"error_code" text,
	"error_detail" text,
	"uploaded_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "document_user_sha256_unique" UNIQUE("user_id","sha256")
);
--> statement-breakpoint
ALTER TABLE "document" ADD CONSTRAINT "document_user_id_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."user"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
CREATE INDEX "document_user_uploaded_idx" ON "document" USING btree ("user_id","uploaded_at");