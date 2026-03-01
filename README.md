# Kollamparambil Family 🏘️✨

A modern, private social platform and directory for the Kollamparambil family. This system features a rich interactive family tree, automated member directory, event management, and a high-end administrative dashboard.

## 🚀 Features

* **Premium Admin UI**: Rebuilt using `django-unfold` with native tabbed layouts, smooth transitions, and professional typography.
* **Smart Sync**: Automated data linkage between Users, Family Members, and Family Heads.
* **Realism Revamp**: Pre-loaded with authentic Indian family data (Son, Daughter, Step-child, Widow, etc.).
* **Interactive Family Tree**: Visual D3.js-powered tree with gender-themed cards, dynamic spacing, and zoom/search/focus.
* **News & Events**: Authenticated users can post news and schedule events.
* **Secure Access**: Invite-only registration with strong password policies (12+ chars).
* **Multi-App Backend**: Segregated apps for `families`, `news`, `profiles`, and `accounts`.
* **Social Media Integration**: Comprehensive Open Graph and Twitter Card support for rich link previews.

## 🌳 Family Tree

The flagship feature — a fully interactive, pan/zoom/searchable genealogy visualisation.

### Visual Design
- **Gender-Coded Cards**: Soft blue tint for males, soft rose for females, gold highlight for logged-in user.
- **Accent Bars & Avatar Rings**: Gradient top bar and coloured rings matching gender palette.
- **Warm Background**: Subtle gradient with decorative cross-pattern overlay.

### Tree Rendering (D3.js)
- **Forest Layout**: Supports multiple disconnected family trees rendered side-by-side.
- **Dynamic Separation**: Spouse-aware spacing algorithm prevents card overlap:
  - Both siblings married → 2.5× base spacing (500px)
  - One sibling married → 2.2× (440px)
  - Unmarried siblings → 1.5× (300px)
- **Dynamic Tree Width**: Each tree's bounds are calculated and offset dynamically (no fixed spacing).
- **Spouse Rendering**: Spouses render as adjacent cards with dashed connector lines.
- **Duplicate Prevention**: Spouse-of-tree-node detection prevents the same member from appearing in multiple trees.

### Relationship Chaining (Backend)
All relationship types are converted to hierarchical `parent` / `spouse` links:

| User Says            | Tree Link Created                                       |
|----------------------|---------------------------------------------------------|
| Father / Mother      | `parent` → direct parent link                           |
| Son / Daughter       | `parent` → user becomes parent of target                |
| Grandparent variants | `parent` → chains through Father/Mother as intermediary |
| Brother / Sister     | `parent` → both become children of shared parent        |
| Uncle / Aunt         | `parent` → becomes child of grandparent                 |
| Cousin               | `parent` → becomes child of uncle/aunt                  |
| Father/Mother-in-law | `parent` → becomes parent of user's spouse              |
| Sister/Brother-in-law| `spouse` → linked to the appropriate sibling            |
| Nephew / Niece       | `parent` → becomes child of user's sibling              |

### Interactive Features
- **Auto-Focus**: Tree smoothly pans and zooms to the logged-in user's card on page load.
- **Search & Focus**: Type a name → dropdown shows matches → click to smoothly pan/zoom to that card.
- **Member Detail Modal**: Click any card to view full profile details.
- **DOB or Age Toggle**: Members can be added with either Date of Birth or direct Age input.
- **"Married To?" Picker**: When adding in-laws, a dropdown lets you specify which sibling they're married to.

## 🌐 Social Media & SEO

* **Open Graph Tags**: Full Facebook and WhatsApp link preview support.
* **Twitter Cards**: Rich preview cards when sharing on Twitter.
* **Consistent Branding**: "Kollamparambil Family" across all pages.
* **Mobile Optimized**: Theme color and mobile-friendly meta tags.

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

### Running Tests

```bash
# Backend (Django)
cd Backend
python manage.py test --verbosity 2

# Frontend (Vitest)
cd Frontend
npx vitest run
```

## 🔑 Personal Admin Login (Internal Testing)

* **URL**: `http://localhost:8000/admin/`
* **Username**: `admin_wesly`
* **Password**: `family_admin_2026`

> [!WARNING]
> Please change this password or delete the user before moving to a production environment.

## 🗺️ Data Relationships

The backend uses a **Smart Sync** architecture:
- **Family**: Core unit for all members.
- **FamilyMember**: Linked 1-to-1 with a **User** account via signals.
- **Relationship**: Directed edge (`from_member → to_member`) with a named type. The tree-builder converts these into hierarchical parent/spouse links.
- **FamilyHead**: Automatically identifies and tracks the head of each family branch.

## 📱 Deployment & Production

- **Docker Ready**: Includes docker-compose.yml for containerized deployment.
- **CI/CD**: GitHub Actions workflows for automated testing and deployment.
- **Traefik Integration**: Automatic SSL/TLS certificate management.
- **Environment Variables**: Secure configuration via .env files.
- **Static Assets**: Optimized for CDN delivery.

## 🛡️ License

Private - For Kollamparambil Family use only.
