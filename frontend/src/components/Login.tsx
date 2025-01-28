import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

interface LoginProps {
  darkMode: boolean;
  toggleDarkMode: () => void;
  onLogin: (token: string) => void; // Add this prop to handle token from parent
}

const Login: React.FC<LoginProps> = ({ darkMode, onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate(); // For redirecting after successful login

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (username === '' || password === '') {
      setError('Please fill in all fields.');
      return;
    }
    setError('');
    try {
      // Sending the request in the format required by OAuth2PasswordRequestForm (form-encoded)
      const response = await fetch('http://localhost:8000/users/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded', // Changed to form-encoded
        },
        body: new URLSearchParams({
          username,
          password,
        }), // Form data encoding
      });

      if (response.ok) {
        const { access_token } = await response.json();
        localStorage.setItem('token', access_token);
        onLogin(access_token); // Update parent component with the token
        navigate('/dashboard'); // Redirect to Dashboard page
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Login failed'); // `detail` is the common error field in FastAPI
      }
    } catch (error) {
      console.error('Error logging in:', error);
      setError('An error occurred. Please try again.');
    }
  };

  return (
    <div className={`flex items-center justify-center min-h-screen ${darkMode ? 'bg-login-dark' : 'bg-login-light'}`}>
      <div className={`bg-white dark:bg-gray-800 p-8 rounded-lg shadow-md w-full max-w-md`}>
        <h2 className={`text-2xl font-bold mb-6 text-center ${darkMode ? 'text-white' : 'text-blue-600'}`}>
          Login
        </h2>
        {error && <p className="text-red-500 mb-4">{error}</p>}
        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label htmlFor="username" className={`block mb-2 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>Username</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className={`w-full p-2 border rounded ${darkMode ? 'bg-gray-700 text-white' : 'bg-gray-50 text-gray-900'}`}
              required
            />
          </div>
          <div>
            <label htmlFor="password" className={`block mb-2 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>Password</label>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className={`w-full p-2 border rounded ${darkMode ? 'bg-gray-700 text-white' : 'bg-gray-50 text-gray-900'}`}
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className={`absolute inset-y-0 right-0 flex items-center pr-3 ${darkMode ? 'text-gray-300' : 'text-gray-500'}`}
              >
                {showPassword ? 'Hide' : 'Show'}
              </button>
            </div>
          </div>
          <button
            type="submit"
            className={`w-full py-2 rounded ${darkMode ? 'bg-blue-600 text-white hover:bg-blue-700' : 'bg-blue-600 text-white hover:bg-blue-700'}`}
          >
            Login
          </button>
        </form>
        <div className="mt-4 text-center">
          <Link to="/users/register" className={`text-blue-600 hover:underline ${darkMode ? 'dark:text-blue-400' : ''}`}>Don't have an account? Register</Link>
        </div>
      </div>
    </div>
  );
};

export default Login;
