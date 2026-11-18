import { useState } from "react";

import { api, errorMessage } from "../api/helper";
import type { QueryResponse } from "../types/types";

/** Sends a question and holds the latest answer. */
export function useAsk() {
  const [result, setResult] = useState<QueryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const ask = async (question: string) => {
    setLoading(true);
    setError(null);
    try {
      setResult(await api.query(question));
    } catch (err) {
      setError(errorMessage(err));
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  return { ask, result, loading, error };
}