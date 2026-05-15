from fastapi import HTTPException, status
from sqlmodel import Session

from app.modules.DetallePedido.models import DetallePedido
from app.modules.DetallePedido.schema import DetallePedidoCreate, DetallePedidoPublic, DetallePedidoUpdate,DetallePedidoList
from app.modules.DetallePedido.unit_of_work import DetallePedidoUnitofWork

class DetallePedidoService:

    ##Inicia servecie
    def __init__(self, session: Session) -> None:
        
        self._session = session

##obtenemos un producto por su id sino retruna error 404
    def _get_or_404(self, uow: DetallePedidoUnitofWork, det: int) -> Producto:
        
       
        producto = uow.productos.get_by_id(producto_id)
        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"producto con id={producto_id} no encontrado",
            )
        return producto
   
    ###Obtenemos los activos
    def get_all(self, offset: int = 0, limit: int = 10) -> ProductoList:
        with ProductoUnitofWork(self._session) as uow:
            productos = uow.productos.get_active(
              offset=offset,
               limit=limit
        )

        total = uow.productos.count()

        result = ProductoList(
            data=[
                ProductoPublic.model_validate(i)
                for i in productos
            ],
            total=total,
        )

        return result
        ##obtener ingrediente del produto segun su id
    def get_ingrediente_or_404(self,uow:ProductoUnitofWork, ingrediente_id:int):
        
        ingrediente = uow.ingredientes.get_by_id(ingrediente_id)
        if not ingrediente:
            raise HTTPException(
                status_code=404,
                detail=f"Ingredienet con id={ingrediente_id} no encontrado"
            )
        return ingrediente
    
    def get_categoria_or_404(self,uow:ProductoUnitofWork, categoria_id:int):
        
        categoria = uow.categorias.get_by_id(categoria_id)
        if not categoria:
            raise HTTPException(
                status_code=404,
                detail=f"categoria con id={categoria_id} no encontrado"
            )
        return categoria


##Obten buscar por id

    def get_by_id(self, producto_id: int) -> ProductoPublic:
        
        with ProductoUnitofWork(self._session) as uow:
            producto = self._get_or_404(uow, producto_id)
            result = ProductoPublic.model_validate(producto)

        return result    
    
 
##crea producto

    def create(self, data: ProductoCreate) -> ProductoPublic:
        
       
        with ProductoUnitofWork(self._session) as uow:
           
            self.get_categoria_or_404(uow, data.categoria_id)

            producto = Producto.model_validate(data)
            for ingrediente_id in data.ingrediente_ids: ##recoerre los ingredientes agregados
                 ingrediente= self.get_ingrediente_or_404(uow,ingrediente_id)##si esta presemnete el ingrediente se guarga en ingrediente
                 producto.ingredientes.append(ingrediente) ##guardamos el ingredeinte en ela lista que ira  a la base de datos

           

            
           
            
            uow.productos.add(producto)

            
            result = ProductoPublic.model_validate(producto)

        return result
    

    ###Modificador
    
    def update(self, producto_id: int, data: ProductoUpdate) -> ProductoPublic:
      with ProductoUnitofWork(self._session) as uow:
        producto = self._get_or_404(uow, producto_id)

        # 🔹 Relación muchos a muchos: ingredientes
        if data.ingrediente_ids is not None:
            ingredientes = []

            for ingrediente_id in data.ingrediente_ids:
                ingrediente = self._get_ingrediente_or_404(uow, ingrediente_id)
                ingredientes.append(ingrediente)

            producto.ingredientes.clear()
            producto.ingredientes.extend(ingredientes)

        # 🔹 Categoría
        if data.categoria_id is not None:
            categoria = self._get_categoria_or_404(uow, data.categoria_id)
            producto.categoria = categoria

        # 🔹 Campos simples (excluyendo relaciones)
        patch = data.model_dump(
            exclude_unset=True,
            exclude={"ingrediente_ids", "categoria_id"}
        )

        for field, value in patch.items():
            setattr(producto, field, value)

        uow.productos.add(producto)

      return ProductoPublic.model_validate(producto)


    ##eliminar
    def soft_delete(self, producto_id: int) -> None:
        
        with ProductoUnitofWork(self._session) as uow:
            producto= self.get_or_404(uow, producto_id)
            producto.is_active = False
            uow.productos.add(producto)