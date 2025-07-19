import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Container } from '@mui/material';
import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import WrestlerPage from './pages/WrestlerPage';
import ProfilePage from './pages/ProfilePage';
import SchoolPage from './pages/SchoolPage';
import BracketsPage from './pages/BracketsPage';
import SearchPage from './pages/SearchPage';

function App() {
  return (
    <>
      <Navbar />
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          {/* Legacy wrestler route for backward compatibility */}
          <Route path="/wrestler/:id" element={<WrestlerPage />} />
          {/* New general profile route */}
          <Route path="/profile/:id" element={<ProfilePage />} />
          <Route path="/school/:id" element={<SchoolPage />} />
          <Route path="/brackets" element={<BracketsPage />} />
          <Route path="/brackets/:tournamentId" element={<BracketsPage />} />
          <Route path="/search" element={<SearchPage />} />
        </Routes>
      </Container>
    </>
  );
}

export default App;
