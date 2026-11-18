import type { Source } from "../types/types";

interface SourceCardProps {
  source: Source;
}

/** One cited source: [index], title (linked for URLs), snippet, and match score. */
export function SourceCard({ source }: SourceCardProps) {
  const title = source.title || source.url || "Untitled note";
  const percent = Math.round(source.score * 100);

  return (
    <li id={`source-${source.index}`} className="rounded-md border border-slate-200 p-3">
      <div className="flex items-baseline gap-2">
        <span className="shrink-0 text-xs font-semibold text-slate-500">[{source.index}]</span>
        <div className="min-w-0 flex-1">
          {source.url ? (
            <a
              href={source.url}
              target="_blank"
              rel="noreferrer"
              className="block truncate text-sm font-medium text-slate-900 hover:underline"
              title={source.url}
            >
              {title}
            </a>
          ) : (
            <span className="block truncate text-sm font-medium text-slate-900" title={title}>
              {title}
            </span>
          )}
        </div>
        <span className="shrink-0 text-xs text-slate-500">{percent}% match</span>
      </div>
      <p className="mt-1 line-clamp-3 text-sm text-slate-600">{source.snippet}</p>
    </li>
  );
}
