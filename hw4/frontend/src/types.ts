export type Customer = {
  user_id: number
  name: string
  email: string
  first_name: string | null
  last_name: string | null
}

export type PageContext = {
  page: string
  product_id: string | null
}

export type ChatResponse = {
  reply: string
  products: Product[]
}

export type InventoryItem = {
  size: string
  quantity: number
}

export type Product = {
  product_id: string
  name: string
  garment_type: string
  description: string
  image_file_path: string
  image_url: string
  colors: string[]
  search_tags: string[]
  price: number
  inventory: InventoryItem[]
  total_stock: number
}
