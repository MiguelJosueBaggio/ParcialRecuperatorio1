from fastapi import HTTPException, status
from sqlmodel import Session

from app.modules.Categoria.models import Categoria
from app.modules.Categoria.schemas import CategoriaCreate,CategoriaUpDate,CategoriaPublic,CategoriaList
from app.modules.Categoria.unit_of_work import CategoriaUnitofWork

class CategoriaService:

    ##Inicia servecie
    def __init__(self, session: Session) -> None:
        
        self._session = session

##obtenemos un producto por su id sino retruna error 404
    def _get_or_404(self, uow: CategoriaUnitofWork, categoria_id: int) -> Categoria:
        
       
        categoria = uow.categorias.get_by_id(categoria_id)
        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"cat con id={categoria_id} no encontrado",
            )
        return categoria
   
    ###Obtenemos los activos
    def get_all(self, offset: int = 0, limit: int = 10) -> CategoriaList:
        with CategoriaUnitofWork(self._session) as uow:

         categorias = uow.categorias.get_active(
            offset=offset,
            limit=limit
        )

        total = uow.categorias.count()

        result = CategoriaList(
            data=[
                CategoriaPublic.model_validate(c)
                for c in categorias
            ],
            total=total
        )

        return result
        ##obtener ingrediente del produto segun su id
    
    def _assert_name_unique(self, uow: CategoriaUnitofWork, nombre: str) -> None:
       
        if uow.categorias.get_by_name(nombre):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe una categoria con el nombre '{nombre}'",
            )

##Obten buscar por id para categoria

    def get_by_id(self, categoria_id: int) -> CategoriaPublic:
        """
        Obtiene una categoría por su ID.
        """
        with CategoriaUnitofWork(self._session) as uow:
            categoria = self._get_or_404(uow, categoria_id)
            result = CategoriaPublic.model_validate(categoria)
        return result 
    
    ### obten subcategorioa por id

    def get_subcategoria_by_id(self, subcategoria_id: int) -> CategoriaPublic:
        """
        Obtiene una subcategoría por su ID.
        """
        with CategoriaUnitofWork(self._session) as uow:
            subcategoria = self._get_or_404(uow, subcategoria_id)
            # Aquí puedes validar que efectivamente tenga un parent_id
            if subcategoria.parent_id is None:
                raise ValueError(f"La categoría con id {subcategoria_id} no es una subcategoría")
            result = CategoriaPublic.model_validate(subcategoria)
        return result
 
##crea categoria

    def create(self, data: CategoriaCreate) -> CategoriaPublic:
        
       
        with CategoriaUnitofWork(self._session) as uow:
            self._assert_name_unique(uow,data.nombre)
           
            categoria = Categoria.model_validate(data)
            uow.categorias.add(categoria)

            
            result = CategoriaPublic.model_validate(categoria)

        return result
    

    def update(self, categoria_id: int, data: CategoriaUpDate) -> CategoriaPublic:
     with CategoriaUnitofWork(self._session) as uow:
        categoria = self._get_or_404(uow, categoria_id)

        if data.nombre is not None and data.nombre != categoria.nombre:
            self._assert_name_unique(uow, data.nombre)

        patch = data.model_dump(exclude_unset=True)

        for field, value in patch.items():
            setattr(categoria, field, value)

        uow.categorias.add(categoria)

        return CategoriaPublic.model_validate(categoria)
    ##eliminar
    def soft_delete(self, categoria_id: int) -> None:
        
        with CategoriaUnitofWork(self._session) as uow:
            categoria= self._get_or_404(uow, categoria_id)
            categoria.is_active = False
            uow.categorias.add(categoria)