import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import Login from './components/Login';
import Welcome from './components/Welcome';
import Register from './components/Register';
import Header from './components/Header';
import Footer from './components/Footer';
import DataControl from './components/DataControl';
import Dashboard from './components/Dashboard';
import DataSummarizer from './components/Dashboard_DataSummarizer';
import Settings from './components/Settings';
import PrivateRoute from './components/PrivateRoute'; 
import DataVisualizer from './components/Dashboard_Visualize';
import VisualizationEditPage from './components/Dashboard_Visual_Edit';
import DataCleaner from './components/Dashboard_DataCleaner';
import './App.css';

const App: React.FC = () => {
  const [darkMode, setDarkMode] = useState<boolean>(false);
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [loading, setLoading] = useState<boolean>(true);

  const toggleDarkMode = () => {
    const newMode = !darkMode;
    localStorage.setItem('darkMode', JSON.stringify(newMode));
    setDarkMode(newMode);
  };

  const handleLogin = (token: string) => {
    localStorage.setItem('token', token);
    setToken(token);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
  };

  useEffect(() => {
    const checkToken = async () => {
      const storedToken = localStorage.getItem('token');
      if (storedToken) {
        setToken(storedToken);
      }
      setLoading(false);
    };

    const handleBeforeUnload = () => {
      // Call your logout function
      handleLogout();
    };

    const storedDarkMode = localStorage.getItem('darkMode');
    if (storedDarkMode) {
      setDarkMode(JSON.parse(storedDarkMode));
    };

    checkToken();
    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <Router>
      <div className={`flex flex-col min-h-screen ${darkMode ? 'dark' : ''}`}>
        <Header darkMode={darkMode} toggleDarkMode={toggleDarkMode} token={token} handleLogout={handleLogout} />
        <main className="flex-grow">
          <Routes>
            <Route path="/" element={<Welcome darkMode={darkMode} toggleDarkMode={toggleDarkMode} />} />
            <Route path="/register" element={<Register darkMode={darkMode} toggleDarkMode={toggleDarkMode} />} />
            <Route path="/login" element={<Login darkMode={darkMode} toggleDarkMode={toggleDarkMode} onLogin={handleLogin} />} />
            {/* Protect the Datacontrol route */}
            <Route 
              path="/datacontrol" 
              element={
                <PrivateRoute token={token}>
                  <DataControl darkMode={darkMode} toggleDarkMode={toggleDarkMode}/>
                </PrivateRoute>
              } 
            />
            {/* Protect the Dashboard route */}
            <Route 
              path="/dashboard" 
              element={
                <PrivateRoute token={token}>
                  <Dashboard darkMode={darkMode} toggleDarkMode={toggleDarkMode}/>
                </PrivateRoute>
              } 
            />
            {/* Protect the Data Summarizer route */}
            <Route 
              path="/datasummarizer" 
              element={
                <PrivateRoute token={token}>
                  <DataSummarizer darkMode={darkMode} toggleDarkMode={toggleDarkMode}/>
                </PrivateRoute>
              } 
            />
            {/* Protect the Dashboard Cleaning route */}
            <Route 
              path="/datacleaner" 
              element={
                <PrivateRoute token={token}>
                  <DataCleaner darkMode={darkMode} toggleDarkMode={toggleDarkMode}/>
                </PrivateRoute>
              } 
            />
            {/* Protect the Dashboard Visualization route */}
            <Route 
              path="/visualize" 
              element={
                <PrivateRoute token={token}>
                  <DataVisualizer darkMode={darkMode} toggleDarkMode={toggleDarkMode}/>
                </PrivateRoute>
              } 
            />
            {/* Protect the Dashboard Visualization Editing route */}
            <Route 
              path="/visualize/edit" 
              element={
                <PrivateRoute token={token}>
                  <VisualizationEditPage darkMode={darkMode} toggleDarkMode={toggleDarkMode}/>
                </PrivateRoute>
              } 
            />
            {/* Protect the Settings route */}
            <Route 
              path="/settings" 
              element={
                <PrivateRoute token={token}>
                  <Settings darkMode={darkMode} toggleDarkMode={toggleDarkMode}/>
                </PrivateRoute>
              } 
            />
            {/* Redirect to Dashboard if user is logged in, otherwise Welcome page */}
            <Route path="*" element={token ? <Navigate to="/dashboard" /> : <Navigate to="/" />} />
          </Routes>
            {/* Add additional routes as needed */}
        </main>
        <Footer />
      </div>
    </Router>
  );
};

export default App;
