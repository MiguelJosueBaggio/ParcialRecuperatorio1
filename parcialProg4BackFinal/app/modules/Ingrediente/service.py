from fastapi import HTTPException, status
from sqlmodel import Session

from app.modules.Ingrediente.models import Ingrediente, productoIngredienteLink
from app.modules.Ingrediente.schemas import IngredienteCreate,IngredienteUpsate,IngredientePublic,IngredienteList,ProductoIngredienteCreate,ProductoIngredienteUpdate,ProductoIngredientePublic   
from app.modules.Ingrediente.unit_of_work import IngredienteUnitofWork

class IngredienteService:

    ##Inicia servecie
    def __init__(self, session: Session) -> None:
        
        self._session = session

##obtenemos un ingrediento por su id sino retruna error 404
    def get_or_404(self, uow: IngredienteUnitofWork, ingrediente_id: int) -> Ingrediente:
        
       
        ingrediente = uow.ingredientes.get_by_id(ingrediente_id)
        if not ingrediente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ingrediente con id={ingrediente_id} no encontrado",
            )
        return ingrediente
    ###obtenemos los alergenos activos y da como respuesta un lista de ingredientes publicos
    def get_alergenos(self,offset:int=0,limit:int=10)->IngredienteList:
        with IngredienteUnitofWork(self._session) as uow:
            ingredientes = uow.ingredientes.get_alergenos(offset=offset,limit=limit)
            total = uow.ingredientes.count()

            result = IngredienteList(
                data=[IngredientePublic.model_validate(i) for i in ingredientes],
                total=total,
            )
        
        return result
    ###Obtenemos los activos
    def get_all(self,offset:int=0,limit:int=10)->IngredienteList:
        with IngredienteUnitofWork(self._session) as uow:
            ingredientes = uow.ingredientes.get_active(offset=offset,limit=limit)
            total = uow.ingredientes.count()

            result = IngredienteList(
                data=[IngredientePublic.model_validate(i) for i in ingredientes],
                total=total,
            )
        
        return result
        ##Todos los ingredientes de un producto
    def get_producto_or_404(self,uow:IngredienteUnitofWork, producto_id:int):
        
        producto = uow.productos.get_by_id(producto_id)
        if not producto:
            raise HTTPException(
                status_code=404,
                detail=f"Producto con id={producto_id} no encontrado"
            )
        return producto
    

##Obten buscar por id

    def get_by_id(self, ingrediente_id: int) -> IngredientePublic:
        
        with IngredienteUnitofWork(self._session) as uow:
            ingrediente = self.get_or_404(uow, ingrediente_id)
            result = IngredientePublic.model_validate(ingrediente)

        return result    
    
    


    def create(self, data: IngredienteCreate) -> IngredientePublic:
        
       
        with IngredienteUnitofWork(self._session) as uow:
           
           
            ingrediente = Ingrediente.model_validate(data)
            for producto_id in data.producto_ids:
                producto =  self.get_producto_or_404(uow, producto_id)
                ingrediente.productos.append(producto)

            uow.ingredientes.add(ingrediente)
           

            
            result = IngredientePublic.model_validate(ingrediente)

        return result
    
    def update(self, ingrediente_id: int, data: IngredienteUpsate) -> IngredientePublic:
     with IngredienteUnitofWork(self._session) as uow:
        ingrediente = self.get_or_404(uow, ingrediente_id)

        # Validar y actualizar productos si se envió la lista
        if data.producto_ids is not None:
            productos = [
                self.get_producto_or_404(uow, producto_id)
                for producto_id in data.producto_ids
            ]

            # Reemplazar relación muchos a muchos
            ingrediente.productos.clear()
            ingrediente.productos.extend(productos)

        # Actualizar solo campos enviados por el cliente (excepto producto_ids)
        patch = data.model_dump(
            exclude_unset=True,
            exclude={"producto_ids"}
        )

        for field, value in patch.items():
            setattr(ingrediente, field, value)

        uow.ingredientes.add(ingrediente)

     return IngredientePublic.model_validate(ingrediente)
    


    ##eliminar
    def soft_delete(self, ingrediente_id: int) -> None:
        
        with IngredienteUnitofWork(self._session) as uow:
            ingrediente= self.get_or_404(uow, ingrediente_id)
            ingrediente.is_active = False
            uow.ingredientes.add(ingrediente)


    ####logica para manejar productosingredientes

    def create_producto_ingrediente(self, data: ProductoIngredienteCreate) -> ProductoIngredientePublic:

     with IngredienteUnitofWork(self._session) as uow:

        existing = uow.producto_ingredientes.get_by_ids(
            data.ingrediente_id,
            data.producto_id
        )
        if existing:    
                     datos= data.model_dump(exclude_unset=True, exclude={"ingrediente_id","producto_id"})
                     for field, value in datos.items():
                          setattr(existing, field, value)     
                     uow.producto_ingredientes.add(existing)

        

        return ProductoIngredientePublic.model_validate(existing)

       