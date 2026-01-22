# Kollaparambil Family Application

A modern, private social platform and directory for the Kollaparambil family. This application features a rich interactive family tree, event management, news sharing, and a secure member directory.

## 🚀 Features

*   **Interactive Family Tree**: Visual D3.js powered force-directed graph to explore family connections.
*   **Member Directory**: Searchable directory of all family members with detailed profiles.
*   **News & Events**: Authenticated users can post news and schedule events.
*   **Calendar Integration**: "Add to Calendar" button for events (Google Calendar).
*   **Secure Access**: Invite-only registration system using unique Sponsor IDs.
*   **Media Gallery**: Photo sharing and gallery view.
*   **Committee Management**: View current committee members.
*   **Security**: HTTPS, Secure Cookies, Password Strength Meter, and Role-based access.

## 🛠️ Tech Stack

*   **Frontend**: Nuxt 3 (Vue 3), Tailwind CSS, D3.js, Pinia.
*   **Backend**: Django REST Framework (Python), PostgreSQL.
*   **Infrastructure**: Docker Swarm, Traefik (Reverse Proxy), Local Registry.
*   **Deployment**: Zero-downtime rolling updates via automated script.

## 📦 Getting Started

### Prerequisites
*   Docker Desktop (with Swarm enabled or initialized by script)
*   PowerShell (for deployment script)

### Running Locally (Zero Downtime Mode)
We use a **deployment script** that handles building images, pushing to a local registry, and deploying to the Docker Swarm.

```powershell
# 1. Run the deployment script
.\deploy.ps1
```

The application will be available at:
*   **Frontend**: https://localhost (Accept the self-signed certificate warning)
*   **Backend API**: https://localhost/api
*   **Traefik Dashboard**: http://localhost:8080

### Stopping the App
To remove the stack and stop all containers:
```powershell
docker stack rm family_app
```

## 🔄 Development Guidelines

### Database (PostgreSQL)
The application now uses PostgreSQL. Data is persisted in a Docker volume `family_app_postgres_data`. To reset the database, you must remove this volume:
```powershell
docker volume rm family_app_postgres_data
```

### Making Changes
1.  Modify the code in `Frontend/` or `Backend/`.
2.  Run `.\deploy.ps1` again.
3.  Docker Swarm will perform a **rolling update** (Start-First strategy), ensuring the app remains available during the update.

## 🛡️ License

Private - For Kollaparambil Family use only.
