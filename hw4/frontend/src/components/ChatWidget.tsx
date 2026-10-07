import { useEffect, useState } from "react"
import type { FormEvent } from "react"
import { useLocation } from "react-router-dom"
import { ApiError, fetchChatHistory, sendChat } from "../api.ts"
import { useAuth } from "../auth.tsx"
import type { PageContext, Product } from "../types.ts"
import { ProductCard } from "./ProductCard.tsx"

type ChatLine = {
  id: number
  role: "user" | "assistant"
  text: string
  products: Product[]
}

function pageContext(pathname: string): PageContext {
  const match = pathname.match(/^\/products\/([^/]+)$/)
  if (match) {
    return { page: "product", product_id: decodeURIComponent(match[1]) }
  }
  if (pathname === "/") {
    return { page: "home", product_id: null }
  }
  const known = pathname.replace(/^\//, "")
  return { page: known || "home", product_id: null }
}

function suggestionsFor(pathname: string): string[] {
  if (/^\/products\/[^/]+$/.test(pathname)) {
    return [
      "Do you have this in size M?",
      "What colors does this come in?",
      "If my size is out, what is similar and in stock?",
    ]
  }
  return [
    "What hoodies do you have?",
    "Which crewnecks are in stock in size M?",
    "What is the price of Basic Hoodie Big Yale?",
  ]
}

export function ChatWidget() {
  const location = useLocation()
  const { customer, loading: authLoading } = useAuth()
  const [open, setOpen] = useState(false)
  const [draft, setDraft] = useState("")
  const [lines, setLines] = useState<ChatLine[]>([])
  const [pending, setPending] = useState(false)
  const [error, setError] = useState("")
  const [retryText, setRetryText] = useState("")

  useEffect(() => {
    if (authLoading) {
      return
    }
    if (!customer) {
      setLines([])
      return
    }
    let active = true
    fetchChatHistory()
      .then((history) => {
        if (!active) {
          return
        }
        setLines((current) => {
          const local = current.filter((line) => line.id < 0)
          return [
            ...history.map((item) => ({
              id: item.id,
              role: item.role === "user" ? ("user" as const) : ("assistant" as const),
              text: item.content,
              products: item.products,
            })),
            ...local,
          ]
        })
      })
      .catch((reason: unknown) => {
        if (active) {
          setError(reason instanceof ApiError ? reason.message : "Saved chat could not be loaded.")
        }
      })
    return () => {
      active = false
    }
  }, [authLoading, customer])

  async function ask(message: string, fromRetry = false) {
    const text = message.trim()
    if (!text || pending) {
      return
    }
    setError("")
    setRetryText("")
    setDraft("")
    setPending(true)
    if (!fromRetry) {
      setLines((current) => [...current, { id: -Date.now(), role: "user", text, products: [] }])
    }
    try {
      const response = await sendChat(text, pageContext(location.pathname))
      setLines((current) => [
        ...current,
        { id: -Date.now(), role: "assistant", text: response.reply, products: response.products },
      ])
    } catch (reason: unknown) {
      setRetryText(text)
      setError(reason instanceof ApiError ? reason.message : "Ask Dan could not answer. Use Retry to ask again.")
    } finally {
      setPending(false)
    }
  }

  async function send(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    await ask(draft)
  }

  const hasCards = lines.some((line) => line.products.length > 0)
  const suggestions = suggestionsFor(location.pathname)

  return (
    <div className="chat-dock">
      {open ? (
        <section className={hasCards ? "chat-panel has-cards" : "chat-panel"} aria-label="Ask Dan">
          <header>
            <div className="chat-identity">
              <img className="dan-avatar" src="/dan-avatar.jpg" alt="" />
              <div>
                <h2>Ask Dan</h2>
                <p>Campus Customs shop dog</p>
              </div>
            </div>
            <button type="button" onClick={() => setOpen(false)} aria-label="Close Ask Dan">
              Close
            </button>
          </header>
          <div className="chat-log">
            {lines.length === 0 && !pending ? (
              <p className="chat-empty">Say hello, or start with a question.</p>
            ) : (
              lines.map((line) => (
                <div key={line.id} className={line.role === "user" ? "chat-user" : "chat-assistant"}>
                  <p>{line.text}</p>
                  {line.products.length > 0 ? (
                    <div className="chat-products">
                      {line.products.map((product) => (
                        <ProductCard key={product.product_id} product={product} />
                      ))}
                    </div>
                  ) : null}
                </div>
              ))
            )}
            {pending ? <p className="chat-pending">Dan is thinking…</p> : null}
          </div>
          {error ? (
            <p className="chat-error">
              {error}
              {retryText ? (
                <button type="button" className="chat-retry" onClick={() => void ask(retryText, true)} disabled={pending}>
                  Retry
                </button>
              ) : null}
            </p>
          ) : null}
          <form onSubmit={(event) => void send(event)}>
            <div className="chat-suggestions">
              {suggestions.map((question) => (
                <button key={question} type="button" onClick={() => void ask(question)} disabled={pending}>
                  {question}
                </button>
              ))}
            </div>
            <label htmlFor="ask-dan">Message</label>
            <div className="chat-compose">
              <input
                id="ask-dan"
                value={draft}
                onChange={(event) => setDraft(event.target.value)}
                placeholder="Ask about the shop"
                disabled={pending}
              />
              <button type="submit" disabled={pending}>
                {pending ? "Sending…" : "Send"}
              </button>
            </div>
          </form>
        </section>
      ) : null}
      <button type="button" className="chat-launcher" aria-expanded={open} onClick={() => setOpen((value) => !value)}>
        <img className="dan-avatar dan-avatar-small" src="/dan-avatar.jpg" alt="" />
        Ask Dan
      </button>
    </div>
  )
}
