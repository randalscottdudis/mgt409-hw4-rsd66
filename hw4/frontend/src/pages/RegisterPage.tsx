import { useState } from "react"
import type { FormEvent } from "react"
import { Link, useNavigate } from "react-router-dom"
import { ApiError, registerAccount } from "../api.ts"
import { useAuth } from "../auth.tsx"

export function RegisterPage() {
  const { customer, setCustomer } = useAuth()
  const navigate = useNavigate()
  const [firstName, setFirstName] = useState("")
  const [lastName, setLastName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [confirmation, setConfirmation] = useState("")
  const [error, setError] = useState("")
  const [pending, setPending] = useState(false)

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError("")
    if (password !== confirmation) {
      setError("Password confirmation does not match.")
      return
    }
    setPending(true)
    try {
      const created = await registerAccount({
        first_name: firstName,
        last_name: lastName,
        email,
        password,
        password_confirmation: confirmation,
      })
      setCustomer(created)
      navigate("/")
    } catch (reason: unknown) {
      setError(reason instanceof ApiError ? reason.message : "The account could not be created.")
    } finally {
      setPending(false)
    }
  }

  return (
    <main className="page narrow">
      <p className="eyebrow">Account</p>
      <h1>Create account</h1>
      {customer ? (
        <p>
          You are signed in as {customer.name}. <Link to="/">Back to the shop</Link>
        </p>
      ) : (
        <form className="account-form" onSubmit={(event) => void submit(event)}>
          <label>
            First name
            <input autoComplete="given-name" value={firstName} onChange={(event) => setFirstName(event.target.value)} required />
          </label>
          <label>
            Last name
            <input autoComplete="family-name" value={lastName} onChange={(event) => setLastName(event.target.value)} required />
          </label>
          <label>
            Email
            <input type="email" autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
          </label>
          <label>
            Password
            <input
              type="password"
              autoComplete="new-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              minLength={8}
              required
            />
          </label>
          <label>
            Confirm password
            <input
              type="password"
              autoComplete="new-password"
              value={confirmation}
              onChange={(event) => setConfirmation(event.target.value)}
              minLength={8}
              required
            />
          </label>
          {error ? <p className="notice">{error}</p> : null}
          <button type="submit" className="button" disabled={pending}>
            {pending ? "Creating account…" : "Create account"}
          </button>
          <p>
            Already have an account? <Link to="/login">Log in</Link>
          </p>
        </form>
      )}
    </main>
  )
}
