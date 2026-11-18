import { useState, type FormEvent } from "react";

interface AskPanelProps {
  onAsk: (question: string) => void;
  loading: boolean;
  /** True when there are no ready items to search yet. */
  disabled: boolean;
}

/** Question box for asking over the saved items. Enter submits. */
export function AskPanel({ onAsk, loading, disabled }: AskPanelProps) {
  const [question, setQuestion] = useState("");
  const isEmpty = question.trim() === "";
  const inputDisabled = disabled || loading;

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (isEmpty || inputDisabled) return;
    // Keep the question in the box so it stays visible next to its answer.
    onAsk(question.trim());
  };

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
          placeholder={disabled ? "Waiting for a ready item…" : "What did I save about…?"}
          disabled={inputDisabled}
          aria-label="Question"
          className="min-w-0 flex-1 rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-slate-500 focus:outline-none focus:ring-1 focus:ring-slate-500 disabled:bg-slate-50"
        />
        <button
          type="submit"
          disabled={inputDisabled || isEmpty}
          className="shrink-0 rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700 disabled:cursor-not-allowed disabled:bg-slate-300"
        >
          {loading ? "Asking…" : "Ask"}
        </button>
      </div>

      {disabled && (
        <p className="mt-2 text-sm text-slate-500">
          Add an item and wait until it's <span className="font-medium">Ready</span> to ask
          questions.
        </p>
      )}
    </form>
  );
}
