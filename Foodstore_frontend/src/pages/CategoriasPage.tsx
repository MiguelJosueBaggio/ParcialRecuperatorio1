import React, { useState } from 'react'
import { useCategories, useDeleteCategory } from '../api/service/categories'
import CategoryForm from '../components/CategoryForm'

const CategoriasPage: React.FC = () => {
  const { data, isLoading } = useCategories()
  const del = useDeleteCategory()
  const [editing, setEditing] = useState<any | null>(null)

  return (
    <section className="py-6">
      <div className="container">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Categorias</h2>
          <button onClick={() => setEditing({})} className="px-3 py-1 bg-green-600 text-white rounded">Nuevo</button>
        </div>

        {editing && (
          <div className="mb-4">
            <CategoryForm initial={editing} onSaved={() => setEditing(null)} />
          </div>
        )}

        {isLoading && <p>Cargando...</p>}
        <div className="grid grid-cols-3 gap-4">
          {data?.data?.map((c: any) => (
            <div key={c.id} className="p-4 bg-white rounded shadow">
              <h3 className="font-medium">{c.nombre}</h3>
              <p className="text-sm text-gray-600">{c.descripcion}</p>
              <div className="flex gap-2 mt-2">
                <button onClick={() => setEditing(c)} className="px-2 py-1 bg-blue-500 text-white rounded">Editar</button>
                <button onClick={() => del.mutate(c.id)} className="px-2 py-1 bg-red-500 text-white rounded">Borrar</button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default CategoriasPage
