import React from 'react'
import { createRoot } from 'react-dom/client'  //Renderizar app
import { BrowserRouter } from 'react-router-dom'  //Habilita rutas
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import App from './App'
import './index.css'

const queryClient = new QueryClient()

const root = document.getElementById('root')

if (!root) {
  throw new Error('Root no encontrado')
}

createRoot(root).render(
  <React.StrictMode>
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>
        <App />
      </QueryClientProvider>
    </BrowserRouter>
  </React.StrictMode>
)