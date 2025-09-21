import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Box } from '@mui/material';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import Upload from './pages/Upload';
import StartupDetail from './pages/StartupDetail';
import StartupOverview from './pages/StartupOverview';
import FounderProfiles from './pages/FounderProfiles';
import MarketBenchmarks from './pages/MarketBenchmarks';
import RiskAssessment from './pages/RiskAssessment';
import InterviewAnalysis from './pages/InterviewAnalysis';
import InterviewChat from './pages/InterviewChat';
import InvestmentMemo from './pages/InvestmentMemo';
import FinalEvaluation from './pages/FinalEvaluation';

function App() {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Navbar />
      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/interview-chat" element={<InterviewChat />} />
          <Route path="/startup/:id" element={<StartupDetail />}>
            <Route index element={<StartupOverview />} />
            <Route path="founders" element={<FounderProfiles />} />
            <Route path="benchmarks" element={<MarketBenchmarks />} />
            <Route path="risks" element={<RiskAssessment />} />
            <Route path="interview" element={<InterviewAnalysis />} />
            <Route path="memo" element={<InvestmentMemo />} />
            <Route path="evaluation" element={<FinalEvaluation />} />
          </Route>
        </Routes>
      </Box>
    </Box>
  );
}

export default App;
