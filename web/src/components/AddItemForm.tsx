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

const fieldClass =
  "w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm placeholder:text-slate-500 focus:border-slate-500 focus:outline-none focus:ring-1 focus:ring-slate-500";

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
    <form onSubmit={handleSubmit} className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-slate-900">Add to inbox</h2>

        <div className="inline-flex rounded-md bg-slate-100 p-0.5" role="group">
          {MODES.map((m) => (
            <button
              key={m.value}
              type="button"
              onClick={() => setMode(m.value)}
              aria-pressed={mode === m.value}
              className={`rounded px-3 py-1 text-xs font-medium transition-colors ${
                mode === m.value
                  ? "bg-white text-slate-900 shadow-sm"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              {m.label}
            </button>
          ))}
        </div>
      </div>

      {mode === "note" ? (
        <textarea
          value={note}
          onChange={(e) => setNote(e.target.value)}
          placeholder="Write a note…"
          rows={3}
          aria-label="Note content"
          className={`resize-y ${fieldClass}`}
        />
      ) : (
        <input
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://example.com/article"
          aria-label="URL"
          className={fieldClass}
        />
      )}

      {error && <p className="text-sm text-red-700">{error}</p>}

      <div className="flex justify-end">
        <button
          type="submit"
          disabled={submitting || isEmpty}
          className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-500"
        >
          {submitting ? "Saving…" : "Save"}
        </button>
      </div>
    </form>
  );
}
