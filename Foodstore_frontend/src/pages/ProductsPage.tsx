import React, { useState } from 'react'
import { useProducts, useDeleteProduct } from '../api/service/products'
import ProductCard from '../components/ProductCard'
import ProductForm from '../components/ProductForm'

const ProductsPage: React.FC = () => {
  const { data, isLoading } = useProducts()
  const del = useDeleteProduct()
  const [editing, setEditing] = useState<any | null>(null)

  return (
    <section className="py-6">
      <div className="container">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Productos</h2>
          <button onClick={() => setEditing({})} className="px-3 py-1 bg-green-600 text-white rounded">Nuevo</button>
        </div>

        {editing && (
          <div className="mb-4">
            <ProductForm initial={editing} onSaved={() => setEditing(null)} />
          </div>
        )}

        {isLoading && <p>Cargando...</p>}
        <div className="grid grid-cols-3 gap-4">
          {data?.data?.map((p: any) => (
            <div key={p.id}>
              <p>{p.nombre}</p> 
              <div className="flex gap-2 mt-2">
                <button onClick={() => setEditing(p)} className="px-2 py-1 bg-blue-500 text-white rounded">Editar</button>
                <button onClick={() => del.mutate(p.id)} className="px-2 py-1 bg-red-500 text-white rounded">Borrar</button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default ProductsPage
