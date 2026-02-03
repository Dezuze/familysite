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
*   **Security**: HTTPS, Secure Cookies, Strong Password Policy (12+ chars), and Role-based access.
*   **Data Integrity**: Automated Database Backups and Strict Schema Validation.

## 🛠️ Tech Stack

*   **Frontend**: Nuxt 3 (Vue 3), Tailwind CSS, D3.js, Pinia.
*   **Backend**: Django REST Framework (Python), PostgreSQL.
*   **Deployment**: cPanel Hosting (Python Passenger + Node.js) with Rolling Releases.

## 📦 Getting Started

### Prerequisites
*   Node.js (v20+)
*   Python (v3.10+)
*   PostgreSQL

### Running Locally

**1. Backend**
```bash
cd Backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

**2. Frontend**
```bash
cd Frontend
npm install
npm run dev
```

The application will be available at:
*   **Frontend**: http://localhost:3000
*   **Backend API**: http://localhost:8000

## 🚀 Deployment Guide (cPanel)

<details>
<summary><strong>Click to expand Deployment Instructions</strong></summary>

### 1. Prerequisites
- **cPanel Account** with support for **Python Apps** (via CloudLinux/Passenger) and **Node.js Apps**.
- **PostgreSQL Database** created in cPanel.
- **SSH Access** (recommended).

### 2. Database Setup
1.  Log in to cPanel -> **PostgreSQL Databases**.
2.  Create a new database (e.g., `username_family_db`).
3.  Create a new user (e.g., `username_family_user`) and password.
4.  Add the user to the database with **All Privileges**.

### 3. Rolling Release Setup (Automated)
We use a **Rolling Release** strategy. Pushing to GitHub triggers cPanel to build in a new folder and swap the live site instantly.

1.  **Server Preparation**:
    ```bash
    # SSH into your server
    mkdir -p ~/www/family_app
    # Ensure you have a virtualenv ready or let 'Setup Python App' create one first
    ```

2.  **Configure Script**:
    - Edit `cpanel_deploy.sh` in the repository.
    - Update `APP_BASE` and `VENV_PATH` to match your server paths.

3.  **cPanel Git Control**:
    - Go to **Git™ Version Control** in cPanel.
    - Clone this repository.
    - The `.cpanel.yml` file will automatically trigger `cpanel_deploy.sh` on push.

### 4. Manual Configuration (First Time)
**Backend (Python App)**:
- **Application Root**: `~/www/family_app/current/Backend`
- **Startup File**: `passenger_wsgi.py`
- **Environment Variables** (Set in cPanel):
    - `django_secret_key`, `debug` (False), `allowed_hosts`, `postgres_db`, etc.

**Frontend (Node.js App)**:
- **Application Root**: `~/www/family_app/current/Frontend`
- **Startup File**: `.output/server/index.mjs`
- **Environment Variables**:
    - `API_BASE`: `https://api.yourdomain.com`
    - `NITRO_PRESET`: `node_server`

</details>

## 🔄 Development Guidelines

### Making Changes
1.  Modify the code in `Frontend/` or `Backend/`.
2.  Test locally using the verification commands above.
3.  Push to `main`.
4.  The **CI/CD Pipeline** will run tests.
5.  **cPanel** will pull the changes and execute the Rolling Release script.

## 🛡️ License

Private - For Kollaparambil Family use only.
