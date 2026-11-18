import type { QueryResponse, Source } from "../types/types";

interface AnswerViewProps {
  result: QueryResponse | null;
  loading: boolean;
}

/** Renders "[1]"-style markers in the answer as links to the matching source. */
function AnswerText({ text }: { text: string }) {
  const parts = text.split(/(\[\d+\])/g);
  return (
    <p className="whitespace-pre-wrap text-slate-800">
      {parts.map((part, i) => {
        const match = /^\[(\d+)\]$/.exec(part);
        if (!match) return part;
        return (
          <a
            key={i}
            href={`#source-${match[1]}`}
            className="mx-0.5 rounded bg-slate-100 px-1 text-xs font-medium text-slate-700 hover:bg-slate-200"
          >
            {match[1]}
          </a>
        );
      })}
    </p>
  );
}

function SourceItem({ source }: { source: Source }) {
  const label = source.title || source.url || "Note";
  return (
    <li id={`source-${source.index}`} className="rounded-md border border-slate-200 p-3">
      <div className="flex items-baseline gap-2">
        <span className="shrink-0 text-xs font-semibold text-slate-500">[{source.index}]</span>
        {source.url ? (
          <a
            href={source.url}
            target="_blank"
            rel="noreferrer"
            className="truncate text-sm font-medium text-slate-900 hover:underline"
          >
            {label}
          </a>
        ) : (
          <span className="truncate text-sm font-medium text-slate-900">{label}</span>
        )}
      </div>
      <p className="mt-1 line-clamp-3 text-sm text-slate-600">{source.snippet}</p>
    </li>
  );
}

/** The latest answer and the sources it cites. */
export function AnswerView({ result, loading }: AnswerViewProps) {
  if (loading) {
    return <p className="text-sm text-slate-500">Thinking…</p>;
  }
  if (!result) {
    return (
      <p className="rounded-lg border border-dashed border-slate-300 p-6 text-center text-sm text-slate-500">
        Your answer will appear here.
      </p>
    );
  }

  return (
    <section className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <h2 className="text-lg font-semibold text-slate-900">Answer</h2>
      <div className="mt-2">
        <AnswerText text={result.answer} />
      </div>

      {result.sources.length > 0 && (
        <>
          <h3 className="mt-4 text-sm font-semibold text-slate-700">Sources</h3>
          <ol className="mt-2 space-y-2">
            {result.sources.map((source) => (
              <SourceItem key={source.chunk_id} source={source} />
            ))}
          </ol>
        </>
      )}
    </section>
  );
}
