# Artificial Data Analyst

![Image](https://github.com/user-attachments/assets/9706bc6f-6b7b-40a2-9767-81dc8b9f539c)


## Project Overview

**Artificial Data Analyst** is a web application designed to help users analyze and visualize data using Large Language Models (LLMs). It leverages LIDA (Library for Intelligent Data Analysis) to automatically generate visualizations and infographics from datasets. This application also helps the users to apply feature engineering and feature selection techniques as part of Data Cleaning functionality along with providing a summary of the dataset used. The application includes user authentication, data upload capabilities, data summarization, data cleaning techniques and advanced visualization features.

## Features

- **User Authentication**: Secure JWT-based authentication system with role-based access control
- **Data Upload & Management**: Support for CSV, Excel, and JSON file formats
- **Data Cleaning**: Supports Feature Engineering and Feature selection techniques for the uploaded dataset.
- **Automated Data Analysis**:
  - Data Summarization
  - Goal Generation
  - Visualization Generation
  - Visualization Editing
  - Visualization Explanation
  - Visualization Evaluation and Repair
- **Multiple LLM Provider Support**: Compatible with OpenAI, Azure OpenAI, PaLM, Cohere, local HuggingFace models and ChatGroq Inference models.
- **Interactive Visualizations**: Using libraries like matplotlib, seaborn, altair, and plotly

## Project Structure

### Backend (FastAPI)
- **Core Components**:
  - `auth.py`: JWT authentication and user management
  - `datacontrol.py`: Data upload and management
  - `datasummarizer.py`: Data analysis and summarization
  - `dashboard_visualize.py`: Visualization generation
  - `datacleaner.py`: Data preprocessing and cleaning

### Frontend (React + TypeScript)
- Modern UI built with React and TypeScript
- Tailwind CSS for styling
- Responsive design for various screen sizes

## Installation

### Prerequisites
- Python 3.9+
- Node.js
- MongoDB
- Docker (optional)
- Modified LLMX and LIDA ( if planning to use ChatGroq Inference models) : Refer my GitHub Repositories.

### Environment Variables
Create a `.env` file with:

```bash
MONGODB_URL=<your-mongodb-url>
SECRET_KEY=<your-secret-ke>
GITHUB_TOKEN=<your-github-token>
GITHUB_USERNAME=<your-github-username>
GITHUB_REPO=<your-github-repo>
ALGORITHM=HS256
LANGCHAIN_API_KEY=<your-langchain-key>
GROQ_API_KEY=<your-groq-key>
MODEL_NAME=<your-model-name>
PROVIDER=<your-provider>
LANGCHAIN_TRACING_V2=true
```

Note : Secret key can be generated from secret_key_generator.py.

### Local Development Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd artificial-data-analyst
```

2. Install backend dependencies:

```bash
cd backend
pip install -r requirements.txt
```

3. Copy the Modified LIDA and LLMX repo contents in your site packages or you can directly use them from a seperate folder and modify the imports in code accordingly(for ChatGroq Inference pipeline).

4. Install frontend dependencies:

```bash
cd frontend
npm install
```

5. Run the development servers:

**Backend**

```bash
cd backend
uvicorn main:app --reload
```

**Frontend**

```bash
cd frontend
npm run dev
```

### Docker Deployment

```bash
docker-compose up --build
```

## API Endpoints

### Authentication
- `POST /users/token`: Get access token
- `POST /users/register`: Register new user
- `POST /users/login`: Login existing user

### Data Management
- `GET /datacontrol/get`: Retrieve data
- `POST /datacontrol/create`: Upload data
- `POST /datacontrol/update`: Update data

### Data Cleaning
- `GET /datacleaner/dtaaframe-info`: Get existing dataframe
- `POST /datacleaner/engineering`: Feature Engineering
- `POST /datacleaner/selection`: Feature Selection

### Analysis
- `POST /datasummarizer`: Generate data summary
- `POST /visualize/goalgenerator`: Generate visualization goals
- `POST /visualize/goaladdition`: Adding new visualization goals
- `POST /visualize/visualization-titles`: Generate visualization titles
- `POST /visualize/visualizations`: Generate visualizations
- `POST /visualize/edit-visualizations`: Edit visualizations using Natural Language
- `POST /visualize/explain-visualizations`: Generate Visualization Explanation
- `POST /visualize/evaluate-visualizations`: Evaluate generated visualizations

## Technologies Used

### Backend
- FastAPI
- MongoDB
- LIDA (Library for Intelligent Data Analysis)
- LLMX
- LangChain
- Pandas
- Matplotlib
- Seaborn
- Altair
- Feature Engine

### Frontend
- React
- TypeScript
- Tailwind CSS
- React Icons

### Infrastructure
- Docker
- MongoDB
- GitHub (for data storage)

## Security

- JWT-based authentication
- Role-based access control
- Secure password hashing
- Environment variable protection
- CORS configuration

## Contributing

Please read our contributing guidelines before submitting pull requests.

## License

This project is licensed under the MIT License.

## Acknowledgments

- LIDA library by Microsoft
- Feature Engine framework
- FastAPI framework
- React and its community
