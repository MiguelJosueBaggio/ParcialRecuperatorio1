import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import Header from './components/shares/Header'
import ProductsPage from './pages/ProductsPage'
import IngredientesPage from './pages/IngredientesPage'      //Etructura de navegacion
import CategoriasPage from './pages/CategoriasPage'

const App: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="container">
        <Routes>
          <Route path="/productos" element={<ProductsPage />} />
          <Route path="/ingredientes" element={<IngredientesPage />} />
          <Route path="/categorias" element={<CategoriasPage />} />
          <Route path="/" element={<Navigate to="/productos" replace />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
