# Office Leaks — Corporate Transparency & Workplace Decryption Platform

> **Notice:** The frontend of this project was totally generated with AI, and the backend was typed with AI under my control, supervision, and active monitoring.

Office Leaks is a next-generation corporate transparency platform designed for employees, insiders, and job seekers. The platform enables users to anonymously share and decrypt workplace culture, review salary distributions, report misconduct, rate internal policies, discuss management decisions, and analyze company ratings in a zero-trust, highly secure environment.

---

## 🚀 Key Features

*   **Anonymous Decrypted Reviews:** Share and view insights categorized by Workplace Culture, Salary Data, Misconduct, Internal Policy, Management, Growth, and Interviews.
*   **Discussion Threads:** Nested comments, comment replies, and discussion networks where corporate professionals can interact.
*   **Interactions:** Support for liking reviews/comments and reposting reviews directly to user feeds.
*   **AI-Powered Company Profiling:** Instantly create and profile companies with AI. Powered by **Tavily Search API** (for real-time web verification) and **Groq (Llama 3.3)** for structured data extraction (headquarters address, founded year, logo, website, and social pages).
*   **Decoupled Architecture:** Strict separation of concerns on the backend (`Controller` → `Service` → `Repository`) yielding extreme modularity.
*   **Cloud Infrastructure:** Seamless media storage powered by Cloudflare R2 and high-speed data caching via Redis.

---

## 🛠 Tech Stack

### Backend
*   **Core Framework:** Django 6.0 + Django REST Framework (DRF)
*   **Database:** SQLite 3 (Production-ready abstraction for standard SQL)
*   **AI Search & Summarization:** Groq (Llama 3.3) & Tavily Search Engine
*   **Caching & Task Queueing:** Redis Client (with Huey/Celery capabilities)
*   **Storage Integration:** Boto3 client for Cloudflare R2 bucket storage

### Frontend
*   **Core Build:** Vite + React + TypeScript
*   **Styling:** Tailwind CSS (utility-first, responsive grid systems)
*   **Icons:** Lucide React

---

## 📂 System Architecture

The backend code strictly adheres to a **Three-Layer Decoupling Pattern**:

1.  **API / Controller Layer:** Validates incoming payloads via Serializers/DTOs, routes the parameters directly to the domain service layer, and handles request contexts.
2.  **Service Layer (Domain Logic):** Fully protocol-agnostic. Orchestrates business validation, handles integrations (Tavily/Groq/R2), and manages explicit database transactions (`@transaction.atomic`).
3.  **Repository Layer (Data Access):** Directly executes database queries, aggregates data, and encapsulates ORM operations.

```
[ HTTP Request ] ──> [ API Controller ] ──> [ Service Domain ] ──> [ Repository ] ──> [ Database ]
                            │                      │
                            └──> Custom Handler    └──> Tavily/Groq APIs / R2 Storage
```

---

## 📦 Backend Applications & Modules

### 1. User App (`office_leaks/user`)
*   **Authentication:** State-of-the-art JWT-based authentication with auto-rotation capabilities (using `rest_framework_simplejwt`).
*   **Profiles:** Manage avatars, bios, age, gender-based default avatar settings, and profile details.
*   **Media Upload:** Direct stream uploads of user profile images to Cloudflare R2.

### 2. Company App (`office_leaks/company`)
*   **Company Directory:** Multi-filter directory lists (by industry category, average rating ranges, and name search).
*   **Company Metrics:** Keeps track of current ratings (1.0 to 4.0 scale), verification badges, and social media handles.
*   **AI Profiling Engine:** The `create-ai/` endpoint queries the web using Tavily, prompts Groq to extract the details, maps the data to valid industrial sectors (`CompanyIndustry`), and creates the profile.

### 3. Review App (`office_leaks/review`)
*   **Reviews & Rates:** Tracks workplace ratings, reviews, and categories.
*   **Nested Discussion Threads:** Multi-level comments system.
*   **Interaction Logic:** Optimistic updates in the UI for likes, unlikes, and sharing reviews as posts.

### 4. Notification App (`office_leaks/notification`)
*   Enables notification streams for post interactions, likes, and comment replies.

---

## ⚙️ Setup & Configuration

### Prerequisites
*   Python 3.10+
*   Node.js 18+
*   Redis server (running locally or remotely)

### 1. Backend Setup

1.  Clone the repository and navigate to the project directory.
2.  Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Configure environment variables in a `.env` file inside `office_leaks/office_leaks/`:
    ```env
    SECRET_KEY=your_django_secret_key
    
    # Cloudflare R2 Storage Settings
    R2_ACCESS_KEY_ID=your_access_key
    R2_SECRET_ACCESS_KEY=your_secret_key
    R2_ENDPOINT=https://your_account_id.r2.cloudflarestorage.com
    R2_BASE_URL=https://pub-your_public_domain.r2.dev
    R2_BUCKET_NAME=your_bucket_name
    
    # Redis Cache Settings
    REDIS_URL=redis://127.0.0.1:6379/0
    
    # AI Search & Extraction Keys
    GROQ_API_KEY=gsk_your_groq_api_key
    TAVILY_API_KEY=tvly-your_tavily_api_key
    ```
5.  Apply migrations:
    ```bash
    python manage.py migrate
    ```
6.  Run the development server:
    ```bash
    python manage.py runserver
    ```

### 2. Frontend Setup

1.  Navigate to the frontend directory:
    ```bash
    cd office_leaks_frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Configure `.env.local` if custom API paths are required (defaults to `/api` proxy):
    ```env
    VITE_API_BASE_URL=http://localhost:8000
    ```
4.  Launch the Vite development server:
    ```bash
    npm run dev
    ```
