import React, { useState } from 'react'
import { useCreateProduct, useUpdateProduct } from '../api/service/products'

type ProductFormState = {
  nombre: string
  descripcion: string
  precio_base: number
  imagenes_url: string[]
  stock_cantidad: number
  disponible: boolean
  categoria_id?: number | null
  ingrediente_ids: number[]
}

const ProductForm: React.FC<{ initial?: any; onSaved?: () => void }> = ({
  initial,
  onSaved
}) => {

  const [form, setForm] = useState<ProductFormState>({  //guardad¿e todo el producto
    nombre: initial?.nombre ?? '',
    descripcion: initial?.descripcion ?? '',
    precio_base: initial?.precio_base ?? 0, //indica si creo o actualizo datos
    imagenes_url: initial?.imagenes_url ?? [],
    stock_cantidad: initial?.stock_cantidad ?? 0,
    disponible: initial?.disponible ?? true,
    categoria_id: initial?.categoria_id ?? null,
    ingrediente_ids: initial?.ingrediente_ids ?? []
  })

  const create = useCreateProduct()  //mutationes de crear o de actualizar
  const update = useUpdateProduct(initial?.id ?? 0)

  const saving = create.isPending || update.isPending //estado de guardasde

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      const payload = {
        ...form,
        categoria_id: form.categoria_id || null
      }

      if (initial?.id) {
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
    <form onSubmit={submit} className="space-y-3 bg-white p-4 rounded shadow">

      {/* Nombre */}
      <div>
        <label className="block text-sm">Nombre</label>
        <input
          className="w-full border p-2"
          value={form.nombre}
          onChange={e =>
            setForm({ ...form, nombre: e.target.value })
          }
        />
      </div>

      {/* Descripción */}
      <div>
        <label className="block text-sm">Descripción</label>
        <input
          className="w-full border p-2"
          value={form.descripcion}
          onChange={e =>
            setForm({ ...form, descripcion: e.target.value })
          }
        />
      </div>

      {/* Precio */}
      <div>
        <label className="block text-sm">Precio base</label>
        <input
          type="number"
          className="w-full border p-2"
          value={form.precio_base}
          onChange={e =>
            setForm({
              ...form,
              precio_base: Number(e.target.value)
            })
          }
        />
      </div>

      {/* Stock */}
      <div>
        <label className="block text-sm">Stock</label>
        <input
          type="number"
          className="w-full border p-2"
          value={form.stock_cantidad}
          onChange={e =>
            setForm({
              ...form,
              stock_cantidad: Number(e.target.value)
            })
          }
        />
      </div>

      {/* Disponible */}
      <div className="flex items-center gap-2">
        <input
          type="checkbox"
          checked={form.disponible}
          onChange={e =>
            setForm({
              ...form,
              disponible: e.target.checked
            })
          }
        />
        <label>Disponible</label>
      </div>

      {/* Categoria ID */}
      <div>
        <label className="block text-sm">Categoria ID</label>
        <input
          type="number"
          className="w-full border p-2"
          value={form.categoria_id ?? ''}
          onChange={e =>
            setForm({
              ...form,
              categoria_id: e.target.value
                ? Number(e.target.value)
                : null
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
        {saving ? 'Guardando...' : 'Guardar'}
      </button>

    </form>
  )
}

export default ProductForm