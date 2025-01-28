import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import avatar from "@/assets/zoro_avatar__by_mohdayan123_dg2pju2.jpg";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Switch } from "@/components/ui/switch";
import { FaSun, FaMoon } from 'react-icons/fa'; 
import { HiMenu } from 'react-icons/hi';

interface HeaderProps {
  darkMode: boolean;
  toggleDarkMode: () => void;
  token: string | null;
  handleLogout: () => void;
}

const Header: React.FC<HeaderProps> = ({ darkMode, toggleDarkMode, token, handleLogout }) => {
  const navigate = useNavigate(); // For navigation after logout

  const handleLogoutClick = () => {
    handleLogout(); // Call the logout function from props
    navigate('/login'); // Redirect to login page after logout
  };

  return (
    <header className="w-full bg-blue-500 dark:bg-gray-900 text-white py-4 shadow-md">
      <div className="container mx-auto flex items-center px-4">
        {/* Avatar */}
        <div className="relative mr-4 ml-20">
          <img 
            src={avatar} 
            alt="Avatar" 
            className="w-10 h-10 rounded-full cursor-pointer hover:opacity-80"
          />
          <div className="absolute hidden group-hover:block bg-black text-white text-xs rounded py-1 px-2 top-full mt-2 left-1/2 transform -translate-x-1/2 whitespace-nowrap">
            Created by Aranya Ray
          </div>
        </div>

        {/* Site Title */}
        <h1 className="text-xl font-semibold flex-grow text-center">Artificial Data Analyst</h1>
        
        {/* Dropdown Menu */}
        <DropdownMenu>
            <DropdownMenuTrigger>
                <HiMenu className="text-2xl" />
            </DropdownMenuTrigger>
            <DropdownMenuContent>
                <DropdownMenuLabel>My Account</DropdownMenuLabel>
                <DropdownMenuSeparator />
                {token ? (
                    <>
                        <DropdownMenuItem><Link to="/dashboard">Dashboard</Link></DropdownMenuItem>
                        <DropdownMenuItem><Link to="/datacontrol">Data Control</Link></DropdownMenuItem>
                        <DropdownMenuItem><Link to="/datacleaner">Data Cleaner</Link></DropdownMenuItem>
                        <DropdownMenuItem><Link to="/visualize">Data Visualization</Link></DropdownMenuItem>
                        <DropdownMenuItem><Link to="/settings">Settings</Link></DropdownMenuItem>
                        <DropdownMenuItem onClick={handleLogoutClick}>Logout</DropdownMenuItem>
                        {/* Optionally, you could add more items for authenticated users */}
                    </>
                ) : (
                    <>
                        <DropdownMenuItem><Link to="/login">Login</Link></DropdownMenuItem>
                        <DropdownMenuItem><Link to="/register">Register</Link></DropdownMenuItem>
                        <DropdownMenuItem><Link to="/developer">Developer</Link></DropdownMenuItem>
                    </>
                )}
                <DropdownMenuSeparator />
                <DropdownMenuItem>
                    <div className="flex items-center">
                        <Switch 
                            checked={darkMode}
                            onCheckedChange={toggleDarkMode}
                        />
                        {darkMode ? <FaSun className="text-yellow-500 ml-2" /> : <FaMoon className="text-gray-500 ml-2" />}
                        <span className="ml-2">{darkMode ? 'Light Mode' : 'Dark Mode'}</span>
                    </div>
                </DropdownMenuItem>
            </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
};

export default Header;
