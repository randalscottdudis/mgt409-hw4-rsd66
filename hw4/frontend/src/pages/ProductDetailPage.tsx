import { useEffect, useState } from "react"
import { Link, useParams } from "react-router-dom"
import { ApiError, assetUrl, fetchProduct, formatPrice } from "../api.ts"
import type { Product } from "../types.ts"

export function ProductDetailPage() {
  const { productId } = useParams()
  const [product, setProduct] = useState<Product | null>(null)
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!productId) {
      setError("That product link is missing an id.")
      setLoading(false)
      return
    }
    let active = true
    setLoading(true)
    setError("")
    setProduct(null)
    fetchProduct(productId)
      .then((row) => {
        if (active) {
          setProduct(row)
        }
      })
      .catch((reason: unknown) => {
        if (!active) {
          return
        }
        if (reason instanceof ApiError) {
          setError(reason.message)
          return
        }
        setError(reason instanceof Error ? reason.message : "This product could not be loaded.")
      })
      .finally(() => {
        if (active) {
          setLoading(false)
        }
      })
    return () => {
      active = false
    }
  }, [productId])

  return (
    <main className="page">
      <p className="back-link">
        <Link to="/products">Back to products</Link>
      </p>
      {loading ? <p className="notice">Loading this product…</p> : null}
      {error ? <p className="notice">{error}</p> : null}
      {product ? (
        <article className="detail">
          <img src={assetUrl(product.image_url)} alt={product.name} />
          <div>
            <p className="eyebrow">{product.garment_type}</p>
            <h1>{product.name}</h1>
            <p className="price price-large">{formatPrice(product.price)}</p>
            <p className="full-description">{product.description}</p>
            <h2>Sizes and stock</h2>
            {product.inventory.length === 0 ? (
              <p>No size or stock rows are recorded for this product.</p>
            ) : (
              <table className="stock-table">
                <caption>Available sizes and how many are on hand. Zero means out of stock.</caption>
                <thead>
                  <tr>
                    <th scope="col">Size</th>
                    <th scope="col">On hand</th>
                  </tr>
                </thead>
                <tbody>
                  {product.inventory.map((item) => (
                    <tr key={item.size}>
                      <th scope="row">{item.size}</th>
                      <td>{item.quantity === 0 ? "Out of stock" : item.quantity}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </article>
      ) : null}
    </main>
  )
}
