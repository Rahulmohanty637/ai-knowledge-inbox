import type { ApiErrorBody, IngestRequest, Item, QueryResponse } from "../types/types";

/** An error returned by our API, carrying its status, code and message. */
export class ApiError extends Error {
    readonly status: number;
    readonly code: string;
    readonly details: ApiErrorBody["error"]["details"];

    constructor(status: number, body: ApiErrorBody["error"]) {
        super(body.message);
        this.name = "ApiError";
        this.status = status;
        this.code = body.code;
        this.details = body.details;
    }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
    let response: Response;
    try {
        response = await fetch(`/api${path}`, {
            ...init,
            headers: { "Content-Type": "application/json", ...init?.headers },
        });
    } catch {
        throw new ApiError(0, {
            code: "NETWORK_ERROR",
            message: "Can't reach the server. Is the backend running?",
            details: null,
        });
    }

    const body = await response.json().catch(() => null);
    if (!response.ok) {
        const error = (body as ApiErrorBody | null)?.error ?? {
            code: "HTTP_ERROR",
            message: `Request failed (HTTP ${response.status}).`,
            details: null,
        };
        throw new ApiError(response.status, error);
    }
    return body as T;
}

/** Turn any thrown value into a message we can show the user. */
export function errorMessage(error: unknown): string {
    if (error instanceof ApiError) {
        const firstDetail = error.details?.[0]?.message;
        return firstDetail ? `${error.message}: ${firstDetail}` : error.message;
    }
    return "Something went wrong. Please try again.";
}

export const api = {
    ingest: (payload: IngestRequest) =>
        request<Item>("/ingest", { method: "POST", body: JSON.stringify(payload) }),

    listItems: () => request<{ items: Item[] }>("/items").then((data) => data.items),

    query: (question: string) =>
        request<QueryResponse>("/query", { method: "POST", body: JSON.stringify({ question }) }),
};