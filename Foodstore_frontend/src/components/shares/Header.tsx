import React from 'react'
import { NavLink } from 'react-router-dom'

const Header: React.FC = () => {
  return (
    <header className="bg-white shadow">
      <div className="container flex items-center justify-between py-4">
        <h1 className="text-xl font-semibold">Mi App</h1>
        <nav className="space-x-4">
          <NavLink className={({isActive})=> isActive ? 'font-bold' : ''} to="/productos">Productos</NavLink>
          <NavLink className={({isActive})=> isActive ? 'font-bold' : ''} to="/ingredientes">Ingredientes</NavLink>
          <NavLink className={({isActive})=> isActive ? 'font-bold' : ''} to="/categorias">Categorias</NavLink>
        </nav>
      </div>
    </header>
  )
}

export default Header
