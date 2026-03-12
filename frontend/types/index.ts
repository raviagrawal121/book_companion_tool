// lib/api.ts
// All communication with the FastAPI backend lives here.
// Components never call fetch() directly — they use these functions.

import type {
  SessionStatus,
  ChatResponse,
  VerifyCodeResponse,
  VerifyPurchaseResponse,
} from "@/types"

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

// ── Generic fetch helper ──────────────────────────────────────────────────────

async function apiFetch<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  })

  if (!res.ok) {
    const error = await res.text()
    throw new Error(`API error ${res.status}: ${error}`)
  }

  return res.json() as Promise<T>
}

// ── Session ───────────────────────────────────────────────────────────────────

export async function createSession(): Promise<{ session_id: string }> {
  return apiFetch("/session/new", { method: "POST" })
}

export async function setName(
  session_id: string,
  name: string
): Promise<{ ok: boolean; name: string }> {
  return apiFetch("/session/name", {
    method: "POST",
    body: JSON.stringify({ session_id, name }),
  })
}

export async function getSessionStatus(
  session_id: string
): Promise<SessionStatus> {
  return apiFetch(`/session/status?session_id=${session_id}`)
}

// ── Chat ──────────────────────────────────────────────────────────────────────

export async function sendMessage(
  session_id: string,
  message: string
): Promise<ChatResponse> {
  return apiFetch("/chat", {
    method: "POST",
    body: JSON.stringify({ session_id, message }),
  })
}

// ── Access codes ──────────────────────────────────────────────────────────────

export async function verifyCode(
  session_id: string,
  code: string
): Promise<VerifyCodeResponse> {
  return apiFetch("/verify/code", {
    method: "POST",
    body: JSON.stringify({ session_id, code }),
  })
}

export async function verifyPurchase(
  session_id: string,
  first_name: string,
  email: string,
  order_number: string
): Promise<VerifyPurchaseResponse> {
  return apiFetch("/verify/purchase", {
    method: "POST",
    body: JSON.stringify({ session_id, first_name, email, order_number }),
  })
}