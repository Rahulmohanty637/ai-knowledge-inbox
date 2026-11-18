// Mirrors the backend schemas (server/app/schemas). Keep the two in sync.

export type SourceType = "note" | "url";
export type ItemStatus = "pending" | "ready" | "failed";

export interface Item {
  id: string;
  source_type: SourceType;
  title: string | null;
  url: string | null;
  preview: string;
  status: ItemStatus;
  error: string | null;
  chunk_count: number;
  created_at: string; // ISO 8601, UTC
}

export type IngestRequest =
  | { type: "note"; content: string }
  | { type: "url"; url: string };

export interface Source {
  index: number; // the [n] used in the answer
  item_id: string;
  chunk_id: string;
  source_type: SourceType;
  title: string | null;
  url: string | null;
  snippet: string;
  score: number;
}

export interface QueryResponse {
  answer: string;
  sources: Source[];
}

export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
    details: { field: string; message: string }[] | null;
  };
}