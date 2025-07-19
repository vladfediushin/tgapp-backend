import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Authorize from './pages/Authorize'
import Home from './pages/Home'
import ModeSelect from './pages/ModeSelect'
import Repeat from './pages/Repeat'
import Results from './pages/Results'
import Profile from './pages/Profile'
import Settings from './pages/Settings'
import ExamSettings from './pages/ExamSettings'
import Topics from './pages/Topics'
import Statistics from './pages/Statistics'

const App = () => {
  return (
    <Routes>
      <Route path="/" element={<Authorize />} />
      <Route path="/home" element={<Home />} />
      <Route path="/mode" element={<ModeSelect />} />
      <Route path="/repeat" element={<Repeat />} />
      <Route path="/results" element={<Results />} />
      <Route path="/profile" element={<Profile />} />
      <Route path="/settings" element={<Settings />} />
      <Route path="/exam-settings" element={<ExamSettings />} />
      <Route path="/topics" element={<Topics />} />
      <Route path="/statistics" element={<Statistics />} />
      {/* другие страницы будут добавлены позже */}
    </Routes>
  )
}

export default App