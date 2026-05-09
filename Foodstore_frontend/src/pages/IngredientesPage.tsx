import React, { useState } from 'react'

import {
  useIngredients,
  useDeleteIngredient
} from '../api/service/ingredients'

import IngredientForm from '../components/IngredientForm'

import type { Ingredient } from '../types'


const IngredientesPage: React.FC = () => {

  const {
    data,
    isLoading
  } = useIngredients()

  const del = useDeleteIngredient()

  const [editing, setEditing] =
    useState<Ingredient | null>(null)


  return (

    <section className="py-6">

      <div className="container">

        <div className="
          flex
          items-center
          justify-between
          mb-4
        ">

          <h2 className="
            text-xl
            font-semibold
          ">
            Ingredientes
          </h2>

          <button
            onClick={() =>
              setEditing({
                id: 0,
                nombre: '',
                descripcion: '',
                es_alergeno: false,
                is_active: true,
                producto_ids: []
              })
            }

            className="
              px-3
              py-1
              bg-green-600
              text-white
              rounded
            "
          >
            Nuevo
          </button>

        </div>


        {editing && (

          <div className="mb-4">

            <IngredientForm
              initial={editing}
              onSaved={() =>
                setEditing(null)
              }
            />

          </div>
        )}


        {isLoading && (
          <p>Cargando...</p>
        )}


        <div className="
          grid
          grid-cols-2
          gap-4
        ">

          {data?.data.map((i) => (

            <div
              key={i.id}
              className="
                p-4
                bg-white
                rounded
                shadow
              "
            >

              <h3 className="font-medium">
                {i.nombre}
              </h3>

              <p className="
                text-sm
                text-gray-600
              ">
                {i.descripcion}
              </p>

              <p className="text-xs mt-1">

                {i.es_alergeno
                  ? '⚠️ Alérgeno'
                  : '✅ Seguro'}

              </p>

              <div className="
                flex
                gap-2
                mt-2
              ">

                <button
                  onClick={() =>
                    setEditing(i)
                  }

                  className="
                    px-2
                    py-1
                    bg-blue-500
                    text-white
                    rounded
                  "
                >
                  Editar
                </button>

                <button
                  onClick={() =>
                    del.mutate(i.id)
                  }

                  className="
                    px-2
                    py-1
                    bg-red-500
                    text-white
                    rounded
                  "
                >
                  Borrar
                </button>

              </div>

            </div>

          ))}

        </div>

      </div>

    </section>
  )
}

export default IngredientesPage