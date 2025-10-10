x# README.md for Django + Tailwind LMS Project

# 🎓 Django + Tailwind LMS Project

This is a **Django-based Learning Management System (LMS)** project styled with **Tailwind CSS** using [`django-tailwind`](https://django-tailwind.readthedocs.io/). It demonstrates modern Django setup, frontend integration, and clean project structure.

---

## 🚀 Features

-   Django backend (Python 3)
-   Tailwind CSS integrated via `django-tailwind`
-   Custom templates and static files
-   Fully responsive UI
-   Ready for deployment

---

## 🧩 Prerequisites

Before running the project, make sure you have:

-   **Python 3.8+**
-   **pip** (Python package manager)
-   **Node.js + npm** (for Tailwind)
-   **Git**

---

## ⚙️ Full Setup Instructions

### 1️⃣ Clone the repository

```bash
git clone https://github.com/ShreyanshPadhiyar10/django-lms.git
cd django-lms
```

---

### 2️⃣ Create and activate a virtual environment

#### On Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

#### On macOS / Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3️⃣ Install Python dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Tailwind setup

Move into the Tailwind app folder and install Node packages:

```bash
cd theme/static_src/src
npm install
cd ..
```

If you get an error like:

```
CommandError: It looks like node.js and/or npm is not installed...
```

Then find your npm path:

-   **Windows:**

```bash
where npm
```

-   **macOS/Linux:**

```bash
which npm
```

Then add the following in your `settings.py` (adjust the path accordingly):

```python
NPM_BIN_PATH = r"C:\Program Files\nodejs\npm.cmd"  # Windows example
# or
NPM_BIN_PATH = "/usr/local/bin/npm"  # macOS/Linux example
```

---

### 5️⃣ Install Tailwind

```bash
pip install django-tailwind
```

---

### 5️⃣ Apply database migrations

```bash
python manage.py migrate
```

---

### 6️⃣ Build Tailwind CSS

#### One-time build:

```bash
python manage.py tailwind build
```

#### Live-reload mode (recommended for development):

```bash
python manage.py tailwind start
```

Keep this running if you want Tailwind to automatically rebuild when you edit templates or CSS.

---

### 7️⃣ Run the Django server

In another terminal window:

```bash
python manage.py runserver
```

Then open your browser at: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

### 8️⃣ (Optional) Create superuser for admin

```bash
python manage.py createsuperuser
```

---

### 9️⃣ Common Commands

| Command                           | Description                     |
| --------------------------------- | ------------------------------- |
| `python manage.py tailwind build` | Build Tailwind CSS once         |
| `python manage.py tailwind start` | Watch mode (auto rebuild)       |
| `python manage.py runserver`      | Run Django development server   |
| `pip freeze > requirements.txt`   | Update Python dependencies list |

---

## 🧰 Project Structure

```
django-lms/
├── manage.py
├── LMS/
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── theme/                 # Tailwind app
│   ├── static_src/
│   ├── package.json
│   └── tailwind.config.js
├── app/                   # Main Django app
│   ├── templates/
│   └── static/
├── requirements.txt       # Python dependencies
└── README.md
```

---

## ⚡ Deployment

Before deploying, build and collect static files:

```bash
python manage.py collectstatic
python manage.py tailwind build
```

Then serve your project via any WSGI server (e.g., Gunicorn) or cloud platform.

---

**Made with ❤️ using Django + Tailwind CSS**
