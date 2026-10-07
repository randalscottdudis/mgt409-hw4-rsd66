import { useEffect, useState } from "react"
import { fetchProducts } from "../api.ts"
import { ProductCard } from "../components/ProductCard.tsx"
import type { Product } from "../types.ts"

export function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([])
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let active = true
    fetchProducts()
      .then((rows) => {
        if (active) {
          setProducts(rows)
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
    <main className="page">
      <header className="page-intro">
        <p className="eyebrow">Catalogue</p>
        <h1>Products</h1>
        <p>Each card uses the database photo, name, price, and a short description. Open one for sizes and stock.</p>
      </header>
      {loading ? <p className="notice">Loading the catalogue…</p> : null}
      {error ? <p className="notice">{error}</p> : null}
      <div className="product-grid">
        {products.map((product) => (
          <ProductCard key={product.product_id} product={product} />
        ))}
      </div>
    </main>
  )
}
