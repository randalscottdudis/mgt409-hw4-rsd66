import { useState } from "react"
import type { FormEvent } from "react"
import { Link, useNavigate } from "react-router-dom"
import { ApiError, loginAccount } from "../api.ts"
import { useAuth } from "../auth.tsx"

export function LoginPage() {
  const { customer, setCustomer, logout } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [pending, setPending] = useState(false)

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError("")
    setPending(true)
    try {
      const signedIn = await loginAccount(email, password)
      setCustomer(signedIn)
      navigate("/")
    } catch (reason: unknown) {
      setError(reason instanceof ApiError ? reason.message : "Sign-in failed.")
    } finally {
      setPending(false)
    }
  }

  return (
    <main className="page narrow">
      <p className="eyebrow">Account</p>
      <h1>Log in</h1>
      {customer ? (
        <>
          <p>You are signed in as {customer.name}.</p>
          <button type="button" className="button" onClick={() => void logout()}>
            Log out
          </button>
        </>
      ) : (
        <form className="account-form" onSubmit={(event) => void submit(event)}>
          <label>
            Email
            <input type="email" autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
          </label>
          <label>
            Password
            <input
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </label>
          {error ? <p className="notice">{error}</p> : null}
          <button type="submit" className="button" disabled={pending}>
            {pending ? "Signing in…" : "Log in"}
          </button>
          <p>
            New here? <Link to="/register">Create account</Link>
          </p>
        </form>
      )}
    </main>
  )
}
