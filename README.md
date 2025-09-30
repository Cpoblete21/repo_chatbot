# repo_chatbot
chatbot application that provides intelligent querying and visualization capabilities for repository analysis.
A powerful Configuration Management Database (CMDB) chatbot application that provides intelligent querying and visualization capabilities for repository analysis.

✨ Features
📊 Interactive dashboard built with Dash
📈 Repository metrics visualization and analytics
🤖 AI-powered question answering about repositories
🔄 Multi-repository support
📉 Real-time data visualization with graphs and heatmaps
🛠 Tech Stack
Frontend: Dash (Python)
Backend: Python 3.9
Database: PostgreSQL with pgvector extension
AI: Integration with AI models for repository analysis
📋 Prerequisites
Python 3.9+
PostgreSQL with pgvector extension
Git
🚀 Installation & Setup
Clone the repository:
git clone <repository-url>
cd cmdb_chatbot

Create and activate a virtual environment:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Install dependencies:
pip install -r requirements.txt

Set up PostgreSQL:

Install PostgreSQL
Create a new database
Install pgvector extension
Run the initialization script from init-db/init.sql
Configure environment variables:
Create a .env file with:

AI_API_KEY=your_api_key
AI_MODEL_ID=your_model_id
AI_BASE_URL=your_base_url
AI_CHAT_MODEL=your_chat_model
DB_HOST=localhost
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_PORT=5432

💻 Usage
Start the application:
python -m frontend.app
if you want to analyze other repos you can specify the repo folder path in the main_back module
at the end where it says "folder".

Open your browser and navigate to http://localhost:8050
Select repositories from the dropdown menu
Explore repository metrics in the analytics dashboard
Use the chatbot interface to ask questions about repositories




📁 Project Structure
cmdb_chatbot/
├── frontend/           # Frontend Dash application
│   ├── app.py         # Main application file
│   ├── components.py  # UI components
│   └── assets/        # Static assets and styles
├── backend/           # Backend logic
│   ├── ai_utils.py    # AI integration
│   ├── db_utils.py    # Database utilities
│   └── qa_utils.py    # Q&A processing
    └── main_back.py    # repo meta data extraction 
└── init-db/           # Database initialization scripts
