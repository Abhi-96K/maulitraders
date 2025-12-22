# Mauli Traders - E-commerce & POS System

Mauli Traders is a comprehensive E-commerce platform with an Admin POS and Inventory Management system, built using Django and Django REST Framework.

## Features

- **User Roles**: Admin, Reseller, Customer.
- **Inventory**: Product management with Categories, Brands, and Stock Logs.
- **POS System**: Admin interface for billing, GST calculation, and PDF Invoice generation.
- **E-commerce**: Responsive frontend for customers and resellers (wholesale pricing).
- **Cart & Checkout**: Session-based cart and order placement flow.
- **Dashboard**: Customer/Reseller dashboard to view order history and invoices.

## Tech Stack

- **Backend**: Django 5.x, Django REST Framework.
- **Database**: PostgreSQL (Production), SQLite (Dev).
- **Frontend**: Django Templates, Vanilla CSS, Alpine.js (optional).
- **PDF Generation**: ReportLab.
- **Containerization**: Docker & Docker Compose.

## Setup Instructions

### Local Development

1.  **Clone the repository**:
    ```bash
    git clone <repo-url>
    cd maulitraders
    ```

2.  **Create Virtual Environment**:
    ```bash
    python3.11 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Database Setup**:
    ```bash
    # Set environment variables for local SQLite dev
    export SQL_ENGINE=django.db.backends.sqlite3
    export SQL_DATABASE=db.sqlite3
    
    # Run migrations
    python manage.py migrate
    
    # Create Superuser
    python manage.py createsuperuser
    ```

5.  **Run Server**:
    ```bash
    python manage.py runserver
    ```

6.  **Access Application**:
    - Frontend: http://localhost:8000/
    - Admin Panel: http://localhost:8000/admin/

### Docker Setup

1.  **Build and Run**:
    ```bash
    docker-compose up --build
    ```

2.  **Run Migrations (inside container)**:
    ```bash
    docker-compose exec web python manage.py migrate
    docker-compose exec web python manage.py createsuperuser
    ```

## Project Structure

- `core/`: Homepage and Dashboard views.
- `users/`: Authentication and User models.
- `products/`: Inventory management.
- `orders/`: Order management and Cart logic.
- `billing/`: Invoice generation.
- `templates/`: HTML templates.
- `static/`: CSS and images.

## Deployment

For deployment on VPS (DigitalOcean/AWS):
1.  Use `docker-compose.yml` for production.
2.  Set `DEBUG=False` and `ALLOWED_HOSTS` in `.env`.
3.  Configure Nginx as a reverse proxy.
4.  Use Gunicorn (already in requirements) to serve the app.
