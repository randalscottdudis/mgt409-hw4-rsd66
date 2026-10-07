import { Link } from "react-router-dom"
import { assetUrl, formatPrice, shortDescription } from "../api.ts"
import type { Product } from "../types.ts"

type ProductCardProps = {
  product: Product
}

export function ProductCard({ product }: ProductCardProps) {
  return (
    <article className="product-card">
      <Link to={`/products/${encodeURIComponent(product.product_id)}`}>
        <img src={assetUrl(product.image_url)} alt="" />
        <div className="product-card-body">
          <h2>{product.name}</h2>
          <p className="price">{formatPrice(product.price)}</p>
          <p className="short-description">{shortDescription(product.description)}</p>
          {product.inventory.length === 0 ? (
            <p className="size-note">No sizes recorded</p>
          ) : (
            <ul className="size-badges" aria-label="Recorded sizes">
              {product.inventory.map((item) => (
                <li key={item.size}>
                  <span className={item.quantity > 0 ? "size-badge" : "size-badge size-out"}>
                    {item.size}
                    {item.quantity > 0 ? (
                      <span className="sr-only">{`, ${item.quantity} in stock`}</span>
                    ) : (
                      <span className="size-status"> Out of stock</span>
                    )}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </Link>
    </article>
  )
}
