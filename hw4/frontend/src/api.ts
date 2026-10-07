import type { ChatResponse, Customer, PageContext, Product } from "./types.ts"

const API_BASE = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/$/, "")

export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = "ApiError"
    this.status = status
  }
}

export function assetUrl(path: string): string {
  if (path.startsWith("http://") || path.startsWith("https://")) {
    return path
  }
  return `${API_BASE}${path}`
}

export function formatPrice(price: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(price)
}

export function shortDescription(description: string): string {
  const cleaned = description.replace(/\s+/g, " ").trim()
  const max = 140
  if (cleaned.length <= max) {
    return cleaned
  }
  const slice = cleaned.slice(0, max)
  const cut = slice.lastIndexOf(" ")
  const shortened = slice.slice(0, cut > 40 ? cut : max).trimEnd()
  return `${shortened}…`
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    credentials: "include",
    headers: {
      ...(init?.body ? { "Content-Type": "application/json" } : {}),
      ...init?.headers,
    },
  })
  if (!response.ok) {
    let detail = `Request failed (${response.status})`
    try {
      const body = (await response.json()) as { detail?: string }
      if (typeof body.detail === "string" && body.detail) {
        detail = body.detail
      }
    } catch {
      // Keep the status message when the body is not JSON.
    }
    throw new ApiError(response.status, detail)
  }
  if (response.status === 204) {
    return undefined as T
  }
  return (await response.json()) as T
}

export function fetchProducts(): Promise<Product[]> {
  return request<Product[]>("/api/products")
}

export function fetchProduct(productId: string): Promise<Product> {
  return request<Product>(`/api/products/${encodeURIComponent(productId)}`)
}

export type Registration = {
  first_name: string
  last_name: string
  email: string
  password: string
  password_confirmation: string
}

export function fetchMe(): Promise<Customer | null> {
  return request<Customer>("/api/auth/me").catch((reason: unknown) => {
    if (reason instanceof ApiError && reason.status === 401) {
      return null
    }
    throw reason
  })
}

export function registerAccount(registration: Registration): Promise<Customer> {
  return request<Customer>("/api/auth/register", {
    method: "POST",
    body: JSON.stringify(registration),
  })
}

export function loginAccount(email: string, password: string): Promise<Customer> {
  return request<Customer>("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  })
}

export function logoutAccount(): Promise<void> {
  return request<void>("/api/auth/logout", { method: "POST" })
}

export type ChatHistoryMessage = {
  id: number
  role: string
  content: string
  products: Product[]
  created_at: string
}

export function fetchChatHistory(): Promise<ChatHistoryMessage[]> {
  return request<ChatHistoryMessage[]>("/api/chat/history")
}

export function sendChat(message: string, pageContext: PageContext): Promise<ChatResponse> {
  return request<ChatResponse>("/api/chat", {
    method: "POST",
    body: JSON.stringify({ message, page_context: pageContext }),
  })
}
