import type { QueryResponse } from "../types/types";
import { SourceCard } from "./SourceCard";

interface AnswerViewProps {
  result: QueryResponse | null;
  loading: boolean;
  error: string | null;
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

/** The latest answer and the sources it cites. Renders nothing before the first question. */
export function AnswerView({ result, loading, error }: AnswerViewProps) {
  if (loading) {
    return <p className="text-sm text-slate-500">Thinking…</p>;
  }
  if (error) {
    return <p className="text-sm text-red-600">{error}</p>;
  }
  if (!result) {
    return null;
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
              <SourceCard key={source.chunk_id} source={source} />
            ))}
          </ol>
        </>
      )}
    </section>
  );
}
