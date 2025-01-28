import React from 'react';
import { Navigate } from 'react-router-dom';

interface PrivateRouteProps {
  token: string | null;
  children: React.ReactNode;
}

const PrivateRoute: React.FC<PrivateRouteProps> = ({ token, children }) => {
  if (!token) {
    // Redirect to login if no token is found
    return <Navigate to="/login" />;
  }
  
  return <>{children}</>;
};

export default PrivateRoute;