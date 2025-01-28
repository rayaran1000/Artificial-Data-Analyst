import React from 'react';
import { FaGithub, FaLinkedin, FaTwitter } from 'react-icons/fa';

const Footer: React.FC = () => {
  // Replace these with your actual URLs
  const githubUrl = "https://github.com/rayaran1000";
  const linkedinUrl = "https://www.linkedin.com/in/aranya-ray-46a635156/";
  const twitterUrl = "https://x.com/AranyaRay1998";

  return (
    <footer className="w-full bg-blue-500 dark:bg-gray-900 text-white py-4 mt-auto">
      <div className="container mx-auto flex justify-center items-center px-4">
        {/* Social Icons */}
        <div className="flex space-x-4 items-center">
          <a href={githubUrl} target="_blank" rel="noopener noreferrer" className="bg-white text-blue-500 p-2 rounded-full hover:bg-gray-200">
            <FaGithub size={20} />
          </a>
          <a href={linkedinUrl} target="_blank" rel="noopener noreferrer" className="bg-white text-blue-500 p-2 rounded-full hover:bg-gray-200">
            <FaLinkedin size={20} />
          </a>
          <a href={twitterUrl} target="_blank" rel="noopener noreferrer" className="bg-white text-blue-500 p-2 rounded-full hover:bg-gray-200">
            <FaTwitter size={20} />
          </a>
        </div>
      </div>

      {/* Copyright Text */}
      <div className="container mx-auto text-center text-xs mt-4">
        <p>
          © 2024 Artificial Data Analyst. All rights reserved.
        </p>
      </div>
    </footer>
  );
};

export default Footer;
