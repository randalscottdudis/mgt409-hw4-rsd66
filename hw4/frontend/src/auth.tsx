import { createContext, useContext, useEffect, useState } from "react"
import type { ReactNode } from "react"
import { fetchMe, logoutAccount } from "./api.ts"
import type { Customer } from "./types.ts"

type AuthValue = {
  customer: Customer | null
  loading: boolean
  setCustomer: (customer: Customer | null) => void
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [customer, setCustomer] = useState<Customer | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let active = true
    fetchMe()
      .then((me) => {
        if (active) {
          setCustomer(me)
        }
      })
      .catch(() => {
        if (active) {
          setCustomer(null)
        }
      })
      .finally(() => {
        if (active) {
          setLoading(false)
        }
      })
    return () => {
      active = false
    }
  }, [])

  async function logout() {
    await logoutAccount()
    setCustomer(null)
  }

  return <AuthContext.Provider value={{ customer, loading, setCustomer, logout }}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthValue {
  const value = useContext(AuthContext)
  if (!value) {
    throw new Error("useAuth must be used inside AuthProvider")
  }
  return value
}
