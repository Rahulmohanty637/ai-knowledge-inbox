import { useCallback, useEffect, useState } from "react";

import { api, errorMessage } from "../api/helper";
import type { Item } from "../types/types";

const POLL_INTERVAL_MS = 2000;

/** Loads saved items and keeps polling while any of them is still processing. */
export function useItems() {
    const [items, setItems] = useState<Item[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const refresh = useCallback(
        () =>
            api
                .listItems()
                .then(
                    (data) => {
                        setItems(data);
                        setError(null);
                    },
                    (err: unknown) => setError(errorMessage(err)),
                )
                .finally(() => setLoading(false)),
        [],
    );

    // Initial load.
    useEffect(() => {
        void refresh();
    }, [refresh]);

    // Poll only while something is pending; stop as soon as everything settles.
    const hasPending = items.some((item) => item.status === "pending");
    useEffect(() => {
        if (!hasPending) return;
        const timer = window.setInterval(() => void refresh(), POLL_INTERVAL_MS);
        return () => window.clearInterval(timer);
    }, [hasPending, refresh]);

    return { items, loading, error, refresh };
}