import { useState } from "react";
import type { IngestRequest } from "../types/types";
import { api, errorMessage } from "../api/helper";

export function useIngest(onSaved: () => void) {
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);


    const submit = async (payload: IngestRequest): Promise<boolean> => {
        setSubmitting(true);
        setError(null);
        try {
            await api.ingest(payload);
            onSaved();
            return true;
        } catch (err) {
            setError(errorMessage(err));
            return false;
        } finally {
            setSubmitting(false);
        }
    };

    return { submit, submitting, error }

}