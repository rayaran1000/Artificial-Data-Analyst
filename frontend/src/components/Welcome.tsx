import React from 'react';

interface WelcomeProps {
  darkMode: boolean;
  toggleDarkMode: () => void;
}

const Welcome: React.FC<WelcomeProps> = ({ darkMode, }) => {
  return (
    <div className={`flex flex-col flex-1 justify-center items-center min-h-screen ${darkMode ? 'bg-dark-mode-background' : 'bg-light-mode-background'}`}>
      <div className="text-center bg-opacity-50 dark:bg-opacity-20 bg-white dark:bg-gray-700 p-10 rounded shadow-lg">
        <h1 className="text-4xl font-bold text-blue-600 dark:text-white">
          Welcome to Artificial Data Analyst
        </h1>
        <p className="mt-4 text-gray-600 dark:text-gray-300">
        Harness the power of AI to generate actionable insights, strategic recommendations, and comprehensive data-driven reports for your business! Our advanced analytics platform leverages cutting-edge artificial intelligence to help you make informed decisions, optimize operations, and drive growth. Whether you’re looking to uncover hidden trends, predict future outcomes, or streamline your reporting processes, our AI-powered tools provide the intelligence you need to stay ahead in today’s competitive landscape. Explore how our innovative solutions can transform your data into a powerful asset and unlock new opportunities for success.
        </p>
      </div>
    </div>
  );
};

export default Welcome;
