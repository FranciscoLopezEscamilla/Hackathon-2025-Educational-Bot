# RampUp AI

Hackaton 2025 - Wise assistant for project knowledge

## 🌍 Problem

Despite comprehensive documentation and processes, new joiners still struggle to find critical project information quickly and face delayed or unanswered queries, leading to frustration and knowledge gaps. Inconsistent, impersonal training and staggered start dates make delivering a cohesive, personalized onboarding experience time-consuming and error-prone.

## 💡 Solution

An AI‐driven, retrieval-augmented chatbot ingests all onboarding materials and project files to act as each new joiner’s 24/7 personal assistant—delivering instant, context-aware answers and bite-sized, role-specific micro-training directly within existing collaboration tools, as well as text/visual content generation on demand. This empowers new joiners to self-educate, accelerate ramp-up, and frees up team leads from repetitive training tasks.

## 🧠 How It Works

- Key features:
  - Agentic Functionality
  - Context Aware
  - RAG (Retrieval Augmented Generation)
  - Content Generation (PDFs, Slides, Diagrams, Images)
  - Custom UI
- Tech Stack
  - Frontend: `React / TypeScript / Tailwind`
  - Backend: `Python / LangGraph / OpenAI / FastAPI / Azure Blob Service`

---

## 🎬 Demo

- **Live Demo:** [RampUp AI](https://rampup-ai-api.vercel.app/)
- **Video walkthrough: (WIP)** [Link Here](#)

---

## 🛠️ How to Run It

## **Prerequisites**

- Python 3.8+
- Git
- Node.js (**>= 18.x**) and npm (**>= 9.x**) installed on your machine

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
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_API_VERSION=
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=
GPT_IMAGES_DEPLOYMENT_NAME=
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME=
CONTAINER=
CONN_STR=
AZURE_SEARCH_ENDPOINT=
AZURE_SEARCH_KEY=
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

## Workflow

![alt text](image-1.png)
