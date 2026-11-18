import { useState, type FormEvent } from "react";

interface AskPanelProps {
  onAsk: (question: string) => Promise<void>;
  loading: boolean;
  error: string | null;
  /** False until at least one item is ready to be searched. */
  enabled: boolean;
}

/** Question box for asking over the saved items. */
export function AskPanel({ onAsk, loading, error, enabled }: AskPanelProps) {
  const [question, setQuestion] = useState("");
  const isEmpty = question.trim() === "";

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (isEmpty || loading || !enabled) return;
    // Keep the question visible next to its answer.
    await onAsk(question.trim());
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm"
    >
      <h2 className="text-lg font-semibold text-slate-900">Ask a question</h2>

      <div className="mt-3 flex gap-2">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder={enabled ? "What did I save about…?" : "Waiting for a ready item…"}
          disabled={!enabled}
          aria-label="Question"
          className="min-w-0 flex-1 rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-slate-500 focus:outline-none focus:ring-1 focus:ring-slate-500 disabled:bg-slate-50"
        />
        <button
          type="submit"
          disabled={!enabled || loading || isEmpty}
          className="shrink-0 rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700 disabled:cursor-not-allowed disabled:bg-slate-300"
        >
          {loading ? "Asking…" : "Ask"}
        </button>
      </div>

      {!enabled && (
        <p className="mt-2 text-sm text-slate-500">
          Add an item and wait until it's <span className="font-medium">Ready</span> to ask
          questions.
        </p>
      )}
      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
    </form>
  );
}
