# ⚡ Electricity Billing System
This is a web-based Electricity Billing System built with Python and Django. It provides an interface for customers, staff, support admins, and Utility Providers for administrators to manage customers, record electricity usage, and generate bills. Designed for academic purposes, this system showcases practical use of web frameworks in utility billing.

## 🛠️ Features
- Admin login and authentication
- Customer management (add/update/delete)
- Electricity usage input and billing calculation
- Auto-generated billing reports
- SQLite-backed persistent storage

## 🚀 Run Locally
1. Clone the repository
   ```bash
   git clone https://github.com/ImY1l/Electricity-Billing-System.git
   ```
2. Create and activate a virtual environment
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

> **Note:** Between steps 2 and 3, you may need to run `pip install django` if you don't have the required dependencies.

3. Run migrations
   ```bash
   python manage.py migrate
   ```
4. Start the development server
   ```bash
   python manage.py runserver
   ```
5. Open <http://127.0.0.1:8000/> and use the system
