import React, { useState } from 'react'

import {
  useCreateIngredient,
  useUpdateIngredient
} from '../api/service/ingredients'  //trae rutas para crear ingredientes

import { useProducts } from '../api/service/products' //trae lista de productos

import type {
  Ingredient,
  IngredientCreate
} from '../types/IngredientTypes'


interface Props {
  initial?: Ingredient | null   //si existe estamos esditando
  onSaved?: () => void       // callback si se guarda con exitos  todo esto se convierte en un create o upadate
}


const IngredientForm: React.FC<Props> = ({
  initial,
  onSaved
}) => {

  const { data: productsData } =
    useProducts()

  const [form, setForm] =//estado de formulario guarda lo pedido por el bacckend en el schemma
    useState<IngredientCreate>({

      nombre:
        initial?.nombre ?? '',  //si estan vacios los datos crra si ha edita

      descripcion:
        initial?.descripcion ?? '',

      es_alergeno:
        initial?.es_alergeno ?? false,

      producto_ids:
        initial?.producto_ids ?? [],
    })


  const create =
    useCreateIngredient()  //Mutacion que crea en el servidor

  const update =
    useUpdateIngredient(
      initial?.id ?? 0
    )


  const saving =
    create.isPending ||   //desactiva el boton
    update.isPending


  const submit = async (  //evita el refrsh
    e: React.FormEvent
  ) => {

    e.preventDefault()

    try {

      if (
        initial &&
        initial.id > 0
      ) {

        await update.mutateAsync(form)  //ejecuta la api

      } else {

        await create.mutateAsync(form)
      }

      onSaved?.() //cierra refresca la lista

    } catch (err) {

      console.error(err)
    }
  }


  return (

    <form
      onSubmit={submit}
      className="
        bg-white
        p-4
        rounded
        shadow
        space-y-4
      "
    >

      <div>

        <label className="block mb-1">
          Nombre
        </label>

        <input
          className="
            w-full
            border
            p-2
            rounded
          "

          value={form.nombre}

          onChange={e =>
            setForm({
              ...form,
              nombre: e.target.value
            })
          }
        />

      </div>


      <div>

        <label className="block mb-1">
          Descripción
        </label>

        <textarea
          className="
            w-full
            border
            p-2
            rounded
          "

          value={form.descripcion}

          onChange={e =>
            setForm({
              ...form,
              descripcion: e.target.value
            })
          }
        />

      </div>


      <div className="
        flex
        items-center
        gap-2
      ">

        <input
          type="checkbox"

          checked={form.es_alergeno}

          onChange={e =>
            setForm({
              ...form,
              es_alergeno: e.target.checked
            })
          }
        />

        <label>
          Es alérgeno
        </label>

      </div>


      <div>

        <label className="block mb-1">
          Productos
        </label>

        <select
          multiple   //permite elegir varios productos

          className="
            w-full
            border
            p-2
            rounded
            min-h-[120px]
          "

          value={
            form.producto_ids.map(   //tranaformaer id a string
              String
            )
          }

          onChange={(e) => {

            const values =
              Array.from(
                e.target.selectedOptions,
                option =>
                  Number(option.value)
              )

            setForm({
              ...form,
              producto_ids: values
            })
          }}
        >

          {productsData?.data.map(
            product => (

            <option
              key={product.id}
              value={product.id}
            >
              {product.nombre}
            </option>

          ))}

        </select>

      </div>


      <button
        type="submit"

        disabled={saving}

        className="
          bg-blue-500
          text-white
          px-4
          py-2
          rounded
          hover:bg-blue-600
        "
      >

        {saving
          ? 'Guardando...'
          : 'Guardar'}

      </button>

    </form>
  )
}

export default IngredientForm