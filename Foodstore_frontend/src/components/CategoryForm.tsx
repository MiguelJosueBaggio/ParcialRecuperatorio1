import React, { useState } from 'react'
import {
  useCreateCategory,
  useUpdateCategory,
} from '../api/service/categories'

import type { CategoryCreate } from '../types'

interface Props {
  initial?: any
  onSaved?: () => void
}

const CategoryForm: React.FC<Props> = ({
  initial,
  onSaved,
}) => {

  const isEdit = !!initial?.id

  const [form, setForm] = useState<CategoryCreate>({
    nombre: initial?.nombre ?? '',
    descripcion: initial?.descripcion ?? null,
    imagen_url: initial?.imagen_url ?? null,
    parent_id: initial?.parent_id ?? null,
  })

  const create = useCreateCategory()
  const update = useUpdateCategory(initial?.id)

  const saving =
    create.isPending || update.isPending

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      const payload = {
        ...form,
        descripcion: form.descripcion || null,
        imagen_url: form.imagen_url || null,
        parent_id: form.parent_id || null,
      }

      if (isEdit) {
        await update.mutateAsync(payload)
      } else {
        await create.mutateAsync(payload)
      }

      onSaved?.()
    } catch (err) {
      console.error(err)
    }
  }

  return (
    <form
      onSubmit={submit}
      className="space-y-3 bg-white p-4 rounded shadow"
    >

      {/* Nombre */}
      <div>
        <label className="block text-sm">
          Nombre
        </label>

        <input
          className="w-full border p-2"
          value={form.nombre}
          onChange={(e) =>
            setForm({
              ...form,
              nombre: e.target.value,
            })
          }
        />
      </div>

      {/* Descripción */}
      <div>
        <label className="block text-sm">
          Descripción
        </label>

        <input
          className="w-full border p-2"
          value={form.descripcion ?? ''}
          onChange={(e) =>
            setForm({
              ...form,
              descripcion: e.target.value
            })
          }
        />
      </div>

      {/* Imagen URL */}
      <div>
        <label className="block text-sm">
          Imagen URL
        </label>

        <input
          className="w-full border p-2"
          value={form.imagen_url ?? ''}
          onChange={(e) =>
            setForm({
              ...form,
              imagen_url: e.target.value || null,
            })
          }
        />
      </div>

      {/* Parent ID */}
      <div>
        <label className="block text-sm">
          Parent ID
        </label>

        <input
          type="number"
          className="w-full border p-2"
          value={form.parent_id ?? ''}
          onChange={(e) =>
            setForm({
              ...form,
              parent_id: e.target.value
                ? Number(e.target.value)
                : null,
            })
          }
        />
      </div>

      {/* Botón */}
      <button
        type="submit"
        disabled={saving}
        className="px-3 py-1 bg-blue-500 text-white rounded"
      >
        {isEdit ? 'Actualizar' : 'Crear'}
      </button>

    </form>
  )
}

export default CategoryForm