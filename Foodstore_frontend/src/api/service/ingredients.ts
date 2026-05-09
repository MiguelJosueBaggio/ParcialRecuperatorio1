import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../../utils/request'
import type { Ingredient } from '../../types'

type IngredientListResponse = {
  items: Ingredient[]
  total: number
}

// GET LIST
export const fetchIngredients = async ( //peticion al back
  offset = 0,
  limit = 20
): Promise<IngredientListResponse> => {
  const response = await api.get('/ingredientes', {
    params: { offset, limit },
  })

  return response.data
}

// HOOK LIST
export const useIngredients = (offset = 0, limit = 20) => { //guarda en el cache evita llamadas repetitivas
  return useQuery({
    queryKey: ['ingredients', offset, limit],
    queryFn: () => fetchIngredients(offset, limit),
  })
}

// GET BY ID
export const fetchIngredientById = async (id: number) => {
  const response = await api.get(`/ingredientes/${id}`)
  return response.data
}

// CREATE
export const useCreateIngredient = () => {
  const qc = useQueryClient()

  return useMutation({
    mutationFn: (payload: Partial<Ingredient>) =>
      api.post('/ingredientes', payload),

    onSuccess: () => {
      qc.invalidateQueries({
        queryKey: ['ingredients'],
      })
    },
  })
}

// UPDATE
export const useUpdateIngredient = (id: number) => {
  const qc = useQueryClient()

  return useMutation({
    mutationFn: (payload: Partial<Ingredient>) =>
      api.patch(`/ingredientes/${id}`, payload),

    onSuccess: () => {
      qc.invalidateQueries({
        queryKey: ['ingredients'],
      })
    },
  })
}

// DELETE
export const useDeleteIngredient = () => {
  const qc = useQueryClient()

  return useMutation({
    mutationFn: (id: number) =>
      api.delete(`/ingredientes/${id}`),

    onSuccess: () => {
      qc.invalidateQueries({
        queryKey: ['ingredients'],
      })
    },
  })
}