import { useEffect, useState } from "react"
import { Link } from "react-router-dom"
import { fetchProducts } from "../api.ts"
import { ProductCard } from "../components/ProductCard.tsx"
import type { Product } from "../types.ts"

export function HomePage() {
  const [products, setProducts] = useState<Product[]>([])
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let active = true
    fetchProducts()
      .then((rows) => {
        if (active) {
          setProducts(rows.slice(0, 4))
        }
      })
      .catch((reason: unknown) => {
        if (active) {
          setError(reason instanceof Error ? reason.message : "The catalogue could not be loaded.")
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

  return (
    <main>
      <section className="hero">
        <div className="hero-copy">
          <p className="eyebrow">Yale Bulldog Blue</p>
          <h1>Good dog. Great Yale gear.</h1>
          <p>
            From campus days to game days, find your next favorite Yale hoodie, tee, or sweatshirt. Show your Bulldog
            pride wherever you roam—Handsome Dan will help you sniff out the right fit.
          </p>
          <Link className="button" to="/products">
            Shop Yale Gear
          </Link>
        </div>
        <HeroPhoto />
      </section>
      <section className="band">
        <div className="section-heading">
          <h2>From the shelf</h2>
          <Link to="/products">All products</Link>
        </div>
        {loading ? <p className="notice">Loading the catalogue…</p> : null}
        {error ? <p className="notice">{error}</p> : null}
        <div className="product-grid">
          {products.map((product) => (
            <ProductCard key={product.product_id} product={product} />
          ))}
        </div>
      </section>
    </main>
  )
}

const HERO_PHOTOS = [
  {
    src: "/dan-hero.jpeg",
    alt: "Handsome Dan sitting on campus steps in a graduation cap and a Yale bandana.",
    position: "center 18%",
  },
  {
    src: "/dan-field.jpg",
    alt: "Handsome Dan sitting on turf beside a Yale pennant, a football helmet, and a football.",
    position: "62% 30%",
  },
  {
    src: "/dan-5.avif",
    alt: "A young Handsome Dan in a Yale bandana, sitting in a white dog bed in front of blue Yale banners.",
    position: "center 42%",
  },
]

const HERO_INTERVAL_MS = 8000

function HeroPhoto() {
  const reducedMotion = usePrefersReducedMotion()
  const [index, setIndex] = useState(0)
  const [paused, setPaused] = useState(false)
  const shown = reducedMotion ? 0 : index

  useEffect(() => {
    if (reducedMotion || paused) {
      return
    }
    const timer = window.setInterval(() => {
      setIndex((current) => (current + 1) % HERO_PHOTOS.length)
    }, HERO_INTERVAL_MS)
    return () => window.clearInterval(timer)
  }, [reducedMotion, paused])

  return (
    <figure className="hero-photo">
      {HERO_PHOTOS.map((photo, photoIndex) => {
        const active = photoIndex === shown
        if (reducedMotion && !active) {
          return null
        }
        return (
          <img
            key={photo.src}
            src={photo.src}
            alt={active ? photo.alt : ""}
            aria-hidden={active ? undefined : true}
            className={active ? "is-shown" : undefined}
            style={{ objectPosition: photo.position }}
          />
        )
      })}
      {reducedMotion ? null : (
        <button
          type="button"
          className="hero-toggle"
          aria-pressed={paused}
          onClick={() => setPaused((value) => !value)}
        >
          {paused ? "Play" : "Pause"}
        </button>
      )}
      <PawMark />
    </figure>
  )
}

function usePrefersReducedMotion() {
  const [reduced, setReduced] = useState(() => window.matchMedia("(prefers-reduced-motion: reduce)").matches)

  useEffect(() => {
    const media = window.matchMedia("(prefers-reduced-motion: reduce)")
    const onChange = () => setReduced(media.matches)
    media.addEventListener("change", onChange)
    return () => media.removeEventListener("change", onChange)
  }, [])

  return reduced
}

function PawMark() {
  return (
    <svg className="paw" viewBox="0 0 64 64" aria-hidden="true">
      <ellipse cx="32" cy="42" rx="12" ry="10" fill="#00356b" />
      <ellipse cx="14" cy="24" rx="6" ry="8" fill="#00356b" />
      <ellipse cx="26" cy="16" rx="6" ry="8" fill="#00356b" />
      <ellipse cx="40" cy="16" rx="6" ry="8" fill="#b0893e" />
      <ellipse cx="52" cy="24" rx="6" ry="8" fill="#00356b" />
    </svg>
  )
}
