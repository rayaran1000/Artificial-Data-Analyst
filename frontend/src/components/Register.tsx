import React, { useState } from 'react';
import { Link , useNavigate} from 'react-router-dom';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

interface RegisterProps {
  darkMode: boolean;
  toggleDarkMode: () => void;
}

const Register: React.FC<RegisterProps> = ({ darkMode }) => {
  const [name, setName] = useState('');
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState<'account' | 'password'>('account');
  const navigate = useNavigate();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (name === '' || username === '' || email === '' || password === '' || confirmPassword === '') {
      setError('Please fill in all fields.');
      return;
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    setError('');

    try {
      const response = await fetch('http://localhost:8000/users/register', { // Update URL to match your backend
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, username, email, password }),
      });
      if (response.ok) {
        // Handle successful registration
        alert('Registration successful!');
        navigate('/login');
        
      } else {
        const { message } = await response.json();
        setError(message || 'Registration failed.');
      }
    } catch (error) {
      console.error('Error:', error);
      setError('Registration failed.');
    }
  };

  return (
    <div className={`flex items-center justify-center min-h-screen ${darkMode ? 'bg-register-dark' : 'bg-register-light'}`}>
      <div className={`bg-white dark:bg-gray-800 p-8 rounded-lg shadow-md w-full max-w-md`}>
        <h2 className={`text-2xl font-bold mb-6 text-center ${darkMode ? 'text-white' : 'text-blue-600'}`}>
          Create a New Account
        </h2>
        {error && <p className="text-red-500 mb-4">{error}</p>}
        <Tabs defaultValue="account" className="w-full mb-6">
          <TabsList className="flex justify-center border-b border-gray-200 dark:border-gray-700">
            <TabsTrigger
              value="account"
              className={`p-2 border-b-2 ${activeTab === 'account' ? 'border-blue-600' : 'border-transparent'} text-gray-700 dark:text-gray-300`}
              onClick={() => setActiveTab('account')}
            >
              Account
            </TabsTrigger>
            <TabsTrigger
              value="password"
              className={`p-2 border-b-2 ${activeTab === 'password' ? 'border-blue-600' : 'border-transparent'} text-gray-700 dark:text-gray-300`}
              onClick={() => setActiveTab('password')}
            >
              Password
            </TabsTrigger>
          </TabsList>
          <TabsContent value="account">
            <form onSubmit={handleRegister} className="space-y-4">
              <div>
                <label htmlFor="name" className={`block mb-2 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>Name</label>
                <input
                  type="text"
                  id="name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className={`w-full p-2 border rounded ${darkMode ? 'bg-gray-700 text-white' : 'bg-gray-50 text-gray-900'}`}
                  required
                />
              </div>
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
                <label htmlFor="email" className={`block mb-2 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>Email</label>
                <input
                  type="email"
                  id="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className={`w-full p-2 border rounded ${darkMode ? 'bg-gray-700 text-white' : 'bg-gray-50 text-gray-900'}`}
                  required
                />
              </div>
            </form>
          </TabsContent>
          <TabsContent value="password">
            <form onSubmit={handleRegister} className="space-y-4">
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
              <div>
                <label htmlFor="confirmPassword" className={`block mb-2 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>Re-enter Password</label>
                <input
                  type={showPassword ? 'text' : 'password'}
                  id="confirmPassword"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className={`w-full p-2 border rounded ${darkMode ? 'bg-gray-700 text-white' : 'bg-gray-50 text-gray-900'}`}
                  required
                />
              </div>
            </form>
          </TabsContent>
        </Tabs>
        <button
          type="submit"
          className={`w-full py-2 rounded ${darkMode ? 'bg-blue-600 text-white hover:bg-blue-700' : 'bg-blue-600 text-white hover:bg-blue-700'}`}
          onClick={handleRegister}
        >
          Register
        </button>
        <div className="mt-4 text-center">
          <Link to="/login" className={`text-blue-600 hover:underline ${darkMode ? 'dark:text-blue-400' : ''}`}>Already have an account? Login</Link>
        </div>
      </div>
    </div>
  );
};

export default Register;
