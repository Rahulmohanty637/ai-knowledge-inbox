import { AddItemForm } from "./components/AddItemForm";
import { AnswerView } from "./components/AnswerView";
import { AskPanel } from "./components/AskPanel";
import { ItemList } from "./components/ItemList";
import { useAsk } from "./hooks/useAsk";
import { useIngest } from "./hooks/useIngest";
import { useItems } from "./hooks/useItems";

function App() {
  const { items, loading, error, refresh } = useItems();
  const ingest = useIngest(refresh);
  const ask = useAsk();
  const hasReadyItems = items.some((i) => i.status === "ready");

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto max-w-6xl px-4 py-5">
          <h1 className="text-2xl font-semibold text-slate-900">AI Knowledge Inbox</h1>
          <p className="mt-1 text-sm text-slate-600">
            Save notes and URLs, then ask questions over them.
          </p>
        </div>
      </header>

      <main className="mx-auto grid max-w-6xl gap-6 px-4 py-6 md:grid-cols-2">
        <div className="space-y-6">
          <AddItemForm
            onSubmit={ingest.submit}
            submitting={ingest.submitting}
            error={ingest.error}
          />
          <ItemList items={items} loading={loading} error={error} />
        </div>

        <div className="space-y-6">
          <AskPanel
            onAsk={(question) => void ask.ask(question)}
            loading={ask.loading}
            disabled={!hasReadyItems}
          />
          <AnswerView result={ask.result} loading={ask.loading} error={ask.error} />
        </div>
      </main>
    </div>
  );
}

export default App;
