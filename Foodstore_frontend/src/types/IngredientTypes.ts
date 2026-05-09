export interface IngredientCreate {
  nombre: string
  descripcion: string
  es_alergeno: boolean
  producto_ids: number[]
}

export interface IngredientUpdate {
  nombre?: string
  descripcion?: string
  es_alergeno?: boolean
  is_active?: boolean
  producto_ids?: number[]
}

export interface Ingredient {
  id: number
  nombre: string
  descripcion: string
  es_alergeno: boolean
  is_active: boolean
  producto_ids: number[]
}

export interface IngredientList {
  data: Ingredient[]
  total: number
}