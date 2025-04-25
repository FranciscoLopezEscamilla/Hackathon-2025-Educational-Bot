# Hackaton2025

Hackaton 2025 - Educational Bot

## **Prerequisites**

- Python 3.8+
- Git
- Node.js (**>= 18.x**) and npm (**>= 9.x**) installed on your machine
- npm package manager v10.7.0 or later (typically installed with NodeJS)

## **Getting Started**

### 1. Clone the repository on your machine

```bash
# Clone this repository
git clone https://techinnovation.accenture.com/p.a.rodriguez.canedo/hackaton2025-educationalbot.git
cd Hackaton2025-EducationalBot
```

### 2. API Local Setup

#### Install Python Dependencies

Open a terminal in the root directory and go to `/api` directory:

```bash
cd api
pip install -r requirements.txt
```

#### Environment Variables

Create a `.env` file in the root directory:

```basic
LLAMA_API_KEY=
HUGHINGFACE_TOKEN=
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_API_VERSION=
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=
GPT_IMAGES_DEPLOYMENT_NAME=
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME=
GLOBAL_LLM_SERVICE=
CONTAINER=
CONN_STR=
```

#### Run API

Within the `/api` directory execute the following command:

```bash
uvicorn main:app --reload
```

API should be running as long as the terminal is not closed or halted.

### 3. Webapp Local Environment

#### Install Node Dependencies

Open a new terminal in the root directory of the cloned repository and go to `/webapp` directory:

```bash
cd webapp
npm install
```

#### Add Environment Variables

Create a `.env` file in the `/webapp` directory:

```basic
VITE_API_BASE_URL="http://127.0.0.1:8000"
```

#### Run React Application Locally

Inside `/webapp` directory, run the following script

```bash
npm run dev
```

If run successfully, the terminal will show the local URL the app is hosted at
![alt text](image.png)
