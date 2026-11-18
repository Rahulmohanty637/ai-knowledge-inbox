import type { Item } from "../types/types";

interface ItemCardProps {
  item: Item;
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function StatusBadge({ item }: ItemCardProps) {
  const base = "shrink-0 rounded-full px-2 py-0.5 text-xs font-medium";
  switch (item.status) {
    case "pending":
      return <span className={`${base} bg-slate-100 text-slate-600`}>Processing…</span>;
    case "ready":
      return (
        <span className={`${base} bg-green-100 text-green-700`}>
          Ready · {item.chunk_count} {item.chunk_count === 1 ? "chunk" : "chunks"}
        </span>
      );
    case "failed":
      return <span className={`${base} bg-red-100 text-red-700`}>Failed</span>;
  }
}

/** One saved note or URL, with its processing status. */
export function ItemCard({ item }: ItemCardProps) {
  const isUrl = item.source_type === "url";
  // Title → preview → URL, whichever exists first.
  const title = item.title || item.preview || item.url || "Untitled";

  return (
    <li className="rounded-lg border border-slate-200 bg-white p-3 shadow-sm">
      <div className="flex items-start gap-3">
        <span
          className={`mt-0.5 shrink-0 rounded px-1.5 py-0.5 text-xs font-semibold uppercase ${
            isUrl ? "bg-blue-50 text-blue-700" : "bg-amber-50 text-amber-700"
          }`}
        >
          {isUrl ? "URL" : "Note"}
        </span>

        <div className="min-w-0 flex-1">
          {isUrl && item.url ? (
            <a
              href={item.url}
              target="_blank"
              rel="noreferrer"
              className="block truncate font-medium text-slate-900 hover:underline"
              title={item.url}
            >
              {title}
            </a>
          ) : (
            <p className="truncate font-medium text-slate-900" title={title}>
              {title}
            </p>
          )}
          <p className="mt-0.5 text-xs text-slate-500">{formatDate(item.created_at)}</p>
        </div>

        <StatusBadge item={item} />
      </div>

      {item.status === "failed" && item.error && (
        <p className="mt-2 text-sm text-red-600">{item.error}</p>
      )}
    </li>
  );
}
