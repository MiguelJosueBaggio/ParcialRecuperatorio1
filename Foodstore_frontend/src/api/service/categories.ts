import {
  useQuery,
  useMutation,
  useQueryClient,
} from '@tanstack/react-query'

import api from '../../utils/request'
import type {
  Category,
  CategoryList,
  CategoryCreate,
  CategoryUpdate,
} from '../../types'

const CATEGORIES_KEY = ['categories']

// GET LIST
export const fetchCategories = async (
  offset = 0,
  limit = 20
): Promise<CategoryList> => {
  const response = await api.get('/categorias', {
    params: { offset, limit },
  })

  return response.data
}

// GET BY ID
export const fetchCategoryById = async (
  id: number
): Promise<Category> => {
  const response = await api.get(`/categorias/${id}`)

  return response.data
}

// LIST HOOK
export const useCategories = (
  offset = 0,
  limit = 20
) => {
  return useQuery({
    queryKey: [...CATEGORIES_KEY, offset, limit],
    queryFn: () => fetchCategories(offset, limit),
  })
}

// SINGLE HOOK
export const useCategory = (id: number) => {
  return useQuery({
    queryKey: [...CATEGORIES_KEY, id],
    queryFn: () => fetchCategoryById(id),
    enabled: !!id,
  })
}

// CREATE
export const useCreateCategory = () => {
  const qc = useQueryClient()

  return useMutation({
    mutationFn: (payload: CategoryCreate) =>
      api.post('/categorias', payload),

    onSuccess: () => {
      qc.invalidateQueries({
        queryKey: CATEGORIES_KEY,
      })
    },
  })
}

// UPDATE
export const useUpdateCategory = (id: number) => {
  const qc = useQueryClient()

  return useMutation({
    mutationFn: (payload: CategoryUpdate) =>
      api.patch(`/categorias/${id}`, payload),

    onSuccess: () => {
      qc.invalidateQueries({
        queryKey: CATEGORIES_KEY,
      })
    },
  })
}

// DELETE
export const useDeleteCategory = () => {
  const qc = useQueryClient()

  return useMutation({
    mutationFn: (id: number) =>
      api.delete(`/categorias/${id}`),

    onSuccess: () => {
      qc.invalidateQueries({
        queryKey: CATEGORIES_KEY,
      })
    },
  })
}