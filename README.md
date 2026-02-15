# Kollamparambil Family 🏘️✨

A modern, private social platform and directory for the Kollamparambil family. This system features a rich interactive family tree, automated member directory, event management, and a high-end administrative dashboard.

## 🚀 Features

* **Premium Admin UI**: Rebuilt using `django-unfold` with native tabbed layouts, smooth transitions, and professional typography.
* **Smart Sync**: Automated data linkage between Users, Family Members, and Family Heads.
* **Realism Revamp**: Pre-loaded with authentic Indian family data (Son, Daughter, Step-child, Widow, etc.).
* **Interactive Family Tree**: Visual D3.js powered force-directed graph to explore family connections.
* **News & Events**: Authenticated users can post news and schedule events.
* **Secure Access**: Invite-only registration with strong password policies (12+ chars).
* **Multi-App Backend**: Segregated apps for `families`, `news`, `profiles`, and `accounts`.
* **Social Media Integration**: Comprehensive Open Graph and Twitter Card support for rich link previews on WhatsApp, Facebook, Twitter, and other platforms.

## 🌐 Social Media & SEO

The application includes comprehensive metadata configuration for optimal social media sharing:

* **Open Graph Tags**: Full Facebook and WhatsApp link preview support
* **Twitter Cards**: Rich preview cards when sharing on Twitter
* **Consistent Branding**: "Kollamparambil Family" branding across all pages
* **Mobile Optimized**: Theme color and mobile-friendly meta tags
* **SEO Ready**: Proper meta descriptions, keywords, and robots directives

When sharing links on WhatsApp, Facebook, or Twitter, the preview will automatically display:
- Title: "Kollamparambil Family"
- Description: "Kollamparambil Family Association - Connecting our heritage and future."
- Image: Family logo
- Proper favicon and app metadata

## 🛠️ Tech Stack

* **Frontend**: Nuxt 3 (Vue 3), Tailwind CSS, D3.js, Pinia.
* **Backend**: Django 5.2 (REST Framework), PostgreSQL.
* **Branding**: Inter (UI) & Cinzel (Identity), Fleur De Leah (Script).

## 📦 Getting Started

### Prerequisites
* Node.js (v20+)
* Python (v3.10+)
* PostgreSQL

### Local Setup

**1. Backend**
```bash
cd Backend
python -m venv venv
.\venv\Scripts\Activate  # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_realism  # Seeds professional Indian data
python manage.py runserver
```

**2. Frontend**
```bash
cd Frontend
npm install --legacy-peer-deps
npm run dev
```

The application will be available at: http://localhost:3000

## 🔑 Personal Admin Login (Internal Testing)

For your personal verification, you can use the following high-privilege account:

* **URL**: `http://localhost:8000/admin/`
* **Username**: `admin_wesly`
* **Password**: `family_admin_2026`

> [!WARNING]
> Please change this password or delete the user before moving to a production environment.

## 🗺️ Data Relationships

The backend uses a **Smart Sync** architecture:
- **Family**: Core unit for all members.
- **FamilyMember**: Linked 1-to-1 with a **User** account via signals.
- **FamilyHead**: Automatically identifies and tracks the head of each family branch.
- **Recursive Connections**: Supports parent/child and step-child relationships dynamically.

## 📱 Deployment & Production

- **Docker Ready**: Includes docker-compose.yml for containerized deployment
- **CI/CD**: GitHub Actions workflows for automated testing and deployment
- **Traefik Integration**: Automatic SSL/TLS certificate management
- **Environment Variables**: Secure configuration via .env files
- **Static Assets**: Optimized for CDN delivery

## 🛡️ License

Private - For Kollamparambil Family use only.
