import { useState, type FormEvent } from "react";

import type { IngestRequest, SourceType } from "../types/types";

interface AddItemFormProps {
  onSubmit: (payload: IngestRequest) => Promise<boolean>;
  submitting: boolean;
  error: string | null;
}

const MODES: { value: SourceType; label: string }[] = [
  { value: "note", label: "Note" },
  { value: "url", label: "URL" },
];

/** Lets the user save either a free-text note or a URL. */
export function AddItemForm({ onSubmit, submitting, error }: AddItemFormProps) {
  const [mode, setMode] = useState<SourceType>("note");
  // Separate state per mode, so switching tabs doesn't wipe what was typed.
  const [note, setNote] = useState("");
  const [url, setUrl] = useState("");

  const value = mode === "note" ? note : url;
  const isEmpty = value.trim() === "";

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (isEmpty || submitting) return;

    const submittedMode = mode;
    const payload: IngestRequest =
      submittedMode === "note"
        ? { type: "note", content: note.trim() }
        : { type: "url", url: url.trim() };

    const saved = await onSubmit(payload);
    // Only clear on success, so a failed save doesn't lose the user's input.
    if (saved) {
      if (submittedMode === "note") setNote("");
      else setUrl("");
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm"
    >
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-slate-900">Add to inbox</h2>

        <div className="inline-flex rounded-md border border-slate-200 p-0.5" role="group">
          {MODES.map((m) => (
            <button
              key={m.value}
              type="button"
              onClick={() => setMode(m.value)}
              aria-pressed={mode === m.value}
              className={`rounded px-3 py-1 text-sm font-medium transition-colors ${
                mode === m.value
                  ? "bg-slate-900 text-white"
                  : "text-slate-600 hover:bg-slate-100"
              }`}
            >
              {m.label}
            </button>
          ))}
        </div>
      </div>

      <div className="mt-3">
        {mode === "note" ? (
          <textarea
            value={note}
            onChange={(e) => setNote(e.target.value)}
            placeholder="Paste or write a note…"
            rows={5}
            aria-label="Note content"
            className="w-full resize-y rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-slate-500 focus:outline-none focus:ring-1 focus:ring-slate-500"
          />
        ) : (
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com/article"
            aria-label="URL"
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-slate-500 focus:outline-none focus:ring-1 focus:ring-slate-500"
          />
        )}
      </div>

      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}

      <div className="mt-3 flex justify-end">
        <button
          type="submit"
          disabled={submitting || isEmpty}
          className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700 disabled:cursor-not-allowed disabled:bg-slate-300"
        >
          {submitting ? "Saving…" : "Save"}
        </button>
      </div>
    </form>
  );
}
