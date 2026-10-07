import { NavLink } from "react-router-dom"
import { useAuth } from "../auth.tsx"

const links = [
  { to: "/", label: "Home", end: true },
  { to: "/products", label: "Products", end: false },
  { to: "/about", label: "About Us", end: false },
]

export function Navbar() {
  const { customer, loading, logout } = useAuth()

  return (
    <header className="site-header">
      <div className="header-inner">
        <NavLink to="/" className="brand" end>
          <BulldogMark />
          <span>
            <strong>Bulldog Blue</strong>
            <small>Campus Customs</small>
          </span>
        </NavLink>
        <nav aria-label="Main">
          {links.map((link) => (
            <NavLink key={link.to} to={link.to} end={link.end}>
              {link.label}
            </NavLink>
          ))}
          {loading ? null : customer ? (
            <>
              <span className="who">{customer.name}</span>
              <button type="button" onClick={() => void logout()}>
                Log out
              </button>
            </>
          ) : (
            <>
              <NavLink to="/login">Log in</NavLink>
              <NavLink to="/register">Create account</NavLink>
            </>
          )}
        </nav>
      </div>
    </header>
  )
}

function BulldogMark() {
  return (
    <svg className="bulldog-mark" viewBox="0 0 64 64" aria-hidden="true">
      <circle cx="32" cy="34" r="22" fill="#f6f1e7" />
      <ellipse cx="16" cy="22" rx="8" ry="10" fill="#8a5a32" />
      <ellipse cx="48" cy="22" rx="8" ry="10" fill="#8a5a32" />
      <circle cx="32" cy="36" r="16" fill="#f3efe6" />
      <ellipse cx="32" cy="42" rx="8" ry="6" fill="#d7b89a" />
      <circle cx="26" cy="34" r="2" fill="#1c1915" />
      <circle cx="38" cy="34" r="2" fill="#1c1915" />
      <path d="M24 48c3 3 13 3 16 0" fill="none" stroke="#1c1915" strokeWidth="1.6" strokeLinecap="round" />
      <path d="M18 40h28c2 8-4 14-14 14S16 48 18 40z" fill="#00356b" />
      <text x="32" y="50" textAnchor="middle" fontSize="9" fontFamily="Georgia, serif" fill="#f6f1e7">
        Y
      </text>
    </svg>
  )
}
