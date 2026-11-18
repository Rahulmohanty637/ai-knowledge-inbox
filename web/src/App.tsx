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
    <div className="min-h-screen bg-white md:grid md:grid-cols-[480px_1fr]">
      {/* Sidebar: stays in place on desktop and scrolls on its own. */}
      <aside className="border-b border-slate-200 bg-slate-50 md:sticky md:top-0 md:h-screen md:overflow-y-auto md:border-r md:border-b-0">
        <div className="px-5 pt-5 pb-4">
          <h1 className="text-base font-semibold text-slate-900">AI Knowledge Inbox</h1>
          <p className="mt-0.5 text-xs text-slate-600">
            Save notes and links, then ask questions about them.
          </p>
        </div>

        <div className="border-b border-slate-200 px-5 pb-5">
          <AddItemForm
            onSubmit={ingest.submit}
            submitting={ingest.submitting}
            error={ingest.error}
          />
        </div>

        <div className="px-5 py-4">
          <ItemList items={items} loading={loading} error={error} />
        </div>
      </aside>

      <main className="min-w-0 space-y-6 p-6">
        <AskPanel
          onAsk={(question) => void ask.ask(question)}
          loading={ask.loading}
          disabled={!hasReadyItems}
        />
        <AnswerView result={ask.result} loading={ask.loading} error={ask.error} />
      </main>
    </div>
  );
}

export default App;
