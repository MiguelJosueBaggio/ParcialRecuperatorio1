import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../../utils/request'
import type { Product } from '../../types'

const PRODUCTS_KEY = ['products']

type ProductListResponse = {
  items: Product[]
  total: number
}

// GET LIST
export const fetchProducts = async (
  offset = 0,
  limit = 20
): Promise<ProductListResponse> => {
  const response = await api.get('/productos', {
    params: { offset, limit },
  })

  return response.data
}

// HOOK LIST
export const useProducts = (offset = 0, limit = 20) => {
  return useQuery({
    queryKey: [...PRODUCTS_KEY, offset, limit],
    queryFn: () => fetchProducts(offset, limit),
  })
}

// GET BY ID
export const fetchProductById = async (
  id: number
): Promise<Product> => {
  const response = await api.get(`/productos/${id}`)

  return response.data
}

// CREATE
export const useCreateProduct = () => {
  const qc = useQueryClient()

  return useMutation({
    mutationFn: (payload: Partial<Product>) =>
      api.post('/productos', payload),

    onSuccess: () => {
      qc.invalidateQueries({
        queryKey: PRODUCTS_KEY,
      })
    },
  })
}

// UPDATE
export const useUpdateProduct = (id: number) => {
  const qc = useQueryClient()

  return useMutation({
    mutationFn: (payload: Partial<Product>) =>
      api.patch(`/productos/${id}`, payload),

    onSuccess: () => {
      qc.invalidateQueries({
        queryKey: PRODUCTS_KEY,
      })
    },
  })
}

// DELETE
export const useDeleteProduct = () => {
  const qc = useQueryClient()

  return useMutation({
    mutationFn: (id: number) =>
      api.delete(`/productos/${id}`),

    onSuccess: () => {
      qc.invalidateQueries({
        queryKey: PRODUCTS_KEY,
      })
    },
  })
}