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
  const base =
    "inline-flex shrink-0 items-center gap-1 whitespace-nowrap rounded-full px-2 py-0.5 text-xs font-medium";
  switch (item.status) {
    case "pending":
      return (
        <span className={`${base} bg-slate-100 text-slate-700`}>
          <span aria-hidden="true">◷</span> Processing…
        </span>
      );
    case "ready":
      return (
        <span className={`${base} bg-green-50 text-green-800`}>
          <span aria-hidden="true">✓</span> Ready · {item.chunk_count}{" "}
          {item.chunk_count === 1 ? "chunk" : "chunks"}
        </span>
      );
    case "failed":
      return (
        <span className={`${base} bg-red-50 text-red-700`}>
          <span aria-hidden="true">!</span> Failed
        </span>
      );
  }
}

/** One saved note or URL, with its processing status. */
export function ItemCard({ item }: ItemCardProps) {
  const isUrl = item.source_type === "url";
  // Title → preview → URL, whichever exists first.
  const title = item.title || item.preview || item.url || "Untitled";

  return (
    <li className="flex flex-col gap-1 rounded-lg border border-slate-200 bg-white px-3 py-2.5">
      <div className="flex items-center justify-between gap-2">
        <span className="text-[11px] font-semibold uppercase tracking-wide text-slate-600">
          {isUrl ? "URL" : "Note"}
        </span>
        <StatusBadge item={item} />
      </div>

      {isUrl && item.url ? (
        <a
          href={item.url}
          target="_blank"
          rel="noreferrer"
          title={title}
          className="truncate text-sm font-medium text-indigo-700 underline underline-offset-2 hover:text-indigo-900"
        >
          {title}
        </a>
      ) : (
        <p className="truncate text-sm font-medium text-slate-900" title={title}>
          {title}
        </p>
      )}

      <p className="text-xs text-slate-600">{formatDate(item.created_at)}</p>

      {item.status === "failed" && item.error && (
        <p className="text-xs text-red-700">{item.error}</p>
      )}
    </li>
  );
}
