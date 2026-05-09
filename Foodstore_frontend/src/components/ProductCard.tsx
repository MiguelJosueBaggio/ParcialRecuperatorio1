import React from 'react'
import type { Product } from '../types'

const ProductCard: React.FC<{item: Product}> = ({ item }) => {
  return (
    <div className="p-4 bg-white rounded shadow">
      <h3 className="font-medium">{item.nombre}</h3>
      <p className="text-sm text-gray-600">{item.precio_base != null ? `$ ${item.precio_base}` : 'Sin precio'}</p>
      <p className="text-sm text-gray-500 mt-2">{item.descripcion}</p>
    </div>
  )
}

export default ProductCard
