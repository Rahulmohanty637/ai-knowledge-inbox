import type { Item } from "../types/types";
import { ItemCard } from "./ItemCard";

interface ItemListProps {
  items: Item[];
  loading: boolean;
  error: string | null;
}

/** Saved items, with loading / error / empty states. */
export function ItemList({ items, loading, error }: ItemListProps) {
  let body;
  if (loading && items.length === 0) {
    body = <p className="text-sm text-slate-600">Loading items…</p>;
  } else if (error && items.length === 0) {
    body = <p className="text-sm text-red-700">{error}</p>;
  } else if (items.length === 0) {
    body = (
      <p className="rounded-lg border border-dashed border-slate-300 p-4 text-center text-sm text-slate-600">
        No items yet. Add a note or URL to get started.
      </p>
    );
  } else {
    body = (
      <>
        {/* A failed background refresh shouldn't hide items we already have. */}
        {error && <p className="mb-2 text-sm text-red-700">{error}</p>}
        <ul className="space-y-2">
          {items.map((item) => (
            <ItemCard key={item.id} item={item} />
          ))}
        </ul>
      </>
    );
  }

  return (
    <section>
      <h2 className="mb-2 text-xs font-semibold text-slate-600">
        Your items{items.length > 0 && ` (${items.length})`}
      </h2>
      {body}
    </section>
  );
}
