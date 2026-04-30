import { useState } from 'react'
import { BrowserRouter, Routes, Route} from 'react-router-dom'
import Home from "./pages/Home"
import Game from "./pages/Game"
import useWebSocket from "./hooks/useWebSocket"

function App() {

  const { socketRef } = useWebSocket();

  return (
    <BrowserRouter>
      <Routes>
        <Route path='/' element = {<Home socketRef = {socketRef} />} />
        <Route path='/game' element = {<Game socketRef = {socketRef} />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
