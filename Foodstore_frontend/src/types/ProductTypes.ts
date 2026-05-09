export interface ProductCreate {
  nombre: string
  descripcion: string
  precio_base: number
  imagenes_url: string[]
  stock_cantidad: number
  disponible: boolean
  categoria_id?: number | null
  ingrediente_ids: number[]
}

export interface ProductUpdate {
  nombre?: string
  descripcion?: string
  precio_base?: number
  imagenes_url?: string[]
  stock_cantidad?: number
  disponible?: boolean
  is_active?: boolean
  categoria_id?: number | null
  ingrediente_ids?: number[]
}

export interface Product {
  id: number
  nombre: string
  descripcion: string
  precio_base: number
  imagenes_url: string[]
  stock_cantidad: number
  disponible: boolean
  is_active: boolean
  categoria_id?: number | null
  ingrediente_ids: number[]
}

export interface ProductList {
  data: Product[]
  total: number
}