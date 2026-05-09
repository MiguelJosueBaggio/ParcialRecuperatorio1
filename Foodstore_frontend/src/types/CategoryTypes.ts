export interface CategoryCreate {
  nombre: string
  descripcion?: string
  imagen_url?: string | null
  parent_id?: number | null
}

export interface CategoryUpdate {
  nombre?: string
  descripcion?: string
  imagen_url?: string | null

  is_active?: boolean

  parent_id?: number | null
}

export interface Category {
  id: number

  nombre: string

  descripcion?: string

  imagen_url?: string | null

  is_active: boolean

  parent_id?: number | null

  subcategorias: Category[]

  created_at: string
  updated_at: string

  deleted_at?: string | null
}

export interface CategoryList {
  items: Category[]
  total: number
}