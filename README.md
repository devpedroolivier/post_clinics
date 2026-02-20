<div align="center">
  <img src="https://via.placeholder.com/150x150?text=Logo+Here" alt="POST Clinics Logo" width="150" height="150" />
  <h1>POST Clinics System</h1>
  <p><strong>A full-stack, AI-powered platform for scheduling and managing clinical appointments.</strong></p>

  [![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
  [![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
  [![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
  [![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
  [![OpenAI](https://img.shields.io/badge/OpenAI-412991.svg?style=for-the-badge&logo=OpenAI&logoColor=white)](https://openai.com/)
</div>

<br />

## 📖 About the Project

**POST Clinics System** is a modern, containerized web application designed to digitalize and streamline the workflow of medical and therapeutic clinics. It features a robust Python/FastAPI backend, an interactive React frontend dashboard, and is integrated with AI capabilities to automate scheduling tasks and act as a virtual receptionist.

### ✨ Key Features
- **Interactive Dashboard:** built with React and Vite, featuring a responsive and intuitive layout.
- **Dynamic Calendar (FullCalendar):** robust patient appointment and schedule management.
- **AI Integration (OpenAI Agents):** smart conversational agents to automate patient support and scheduling.
- **Fast & Scalable REST API:** built on top of FastAPI and Pydantic.
- **Asynchronous Database:** utilizing SQLite (via `aiosqlite`) strictly managed by SQLModel.
- **Production-Ready Containerization:** Dockerized setup handling App, Nginx reverse proxy, and SSL generation (Certbot).

---

## 🛠️ Tech Stack

### Backend
- **Framework:** FastAPI
- **Database ORM:** SQLModel / aiosqlite
- **AI Integration:** openai-agents
- **Dependencies:** Uvicorn, Requests, Python-dotenv

### Frontend
- **Framework:** React / TypeScript
- **Bundler:** Vite
- **UI & Interaction:** FullCalendar (timegrid, daygrid, list views)

### Infrastructure
- **Containerization:** Docker & Docker Compose
- **Proxy & Security:** Nginx, Certbot (Let's Encrypt SSL)

---

## 📷 Screenshots / Demo
*(Add screenshots or GIFs of your dashboard, calendar view, and AI interaction here to make your portfolio pop!)*

<details>
<summary>Click to view Screenshots</summary>

*Placeholder for Calendar View*  
![Calendar](https://via.placeholder.com/800x400?text=Interactive+Calendar+View)

*Placeholder for AI Agent Interface*  
![AI Interface](https://via.placeholder.com/800x400?text=Virtual+Receptionist+Chat)

</details>

---

## 🚀 Getting Started

### Prerequisites
- [Docker](https://www.docker.com/get-started) and Docker Compose
- [Node.js](https://nodejs.org/en) & npm (for local frontend development)
- [Python 3.11+](https://www.python.org/downloads/) (for local backend development)

### Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/post-clinics.git
   cd post-clinics
   ```

2. **Environment Configuration:**
   Copy the example environment file and insert your API keys (e.g., OpenAI API Key).
   ```bash
   cp .env.example .env
   ```

3. **Running the Application (Dockerized):**
   ```bash
   docker-compose up --build
   ```
   - **Backend API Docs (Swagger):** `http://localhost:8000/docs`
   - **Frontend Dashboard:** `http://localhost:5173` (or port specified in compose file)

---

## 🌐 Production Deployment (VPS)

To deploy on a VPS (e.g., Hostinger / AWS / DigitalOcean) using Nginx and automatic SSL:

### Setup Requirements
- Docker & Docker Compose installed on VPS.
- Domain `clinics.posolutionstech.com.br` pointing to your VPS IP Address (`A` Record).

### Steps
1. **Clone the repository on the server.**
2. **Create the production `.env` file** based on `.env.example`.
3. **Initialize SSL & Start the Stack:**
   The `docker-compose.prod.yml` spins up the Application, Nginx reverse proxy, and Certbot for SSL termination.
   ```bash
   chmod +x init-letsencrypt.sh
   ./init-letsencrypt.sh
   
   # Or using docker-compose directly:
   docker-compose -f docker-compose.prod.yml up -d --build
   ```

---

## 📂 Project Structure

```text
📁 post_clinics/
├── 📁 src/                  # FastAPI Backend Source Code
│   ├── main.py              # Application Entry Point
│   ├── database.py          # SQLModel Database connection
│   ├── agent.py             # AI Agent implementation (OpenAI)
│   ├── scheduler.py         # Job Scheduler logic
│   ├── tools.py             # Agent tools & functions
│   └── zapi.py              # External integrations
├── 📁 dashboard/            # React + Vite Frontend Application
│   ├── src/
│   └── package.json
├── 📁 nginx/                # Production Reverse Proxy configurations
├── 📁 scripts/              # Useful shell & automation scripts
├── docker-compose.yml       # Local Development Compose File
├── docker-compose.prod.yml  # Production Compose File
└── init-letsencrypt.sh      # SSL Generation Script
```

---

## 🤝 Contributing
Contributions, issues, and feature requests are welcome!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📜 License
This project is licensed under the MIT License - see the `LICENSE` file for details.

---

<div align="center">
  <b>Developed by</b> <a href="https://github.com/your-username">Your Name/Posolutions Tech</a> 🚀
</div>
