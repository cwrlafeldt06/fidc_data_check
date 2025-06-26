import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { BarChart3, FileText } from 'lucide-react';

const Header = () => {
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-2">
            <BarChart3 className="h-8 w-8 text-primary-600" />
            <h1 className="text-xl font-bold text-gray-900">FIDC Analysis Dashboard</h1>
          </div>
          
          <nav className="flex space-x-4">
            <Link
              to="/"
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                isActive('/') 
                  ? 'bg-primary-100 text-primary-700' 
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              <div className="flex items-center space-x-1">
                <FileText className="h-4 w-4" />
                <span>CSV Comparison</span>
              </div>
            </Link>
            
            <Link
              to="/fund-analysis"
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                isActive('/fund-analysis') 
                  ? 'bg-primary-100 text-primary-700' 
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              <div className="flex items-center space-x-1">
                <BarChart3 className="h-4 w-4" />
                <span>Fund Analysis</span>
              </div>
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header; 