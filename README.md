# Boc BackEnd Django

This is a Django project with Django REST framework.

## Prerequisites

- Python 3.x
- pip

## Installation

1. **Clone the repository:**

   ```
   git clone https://github.com/said-grich/boc_backend.git
   cd boc_backend

2. **Clone the repository:**
    ```
    python -m venv boc_env
    boc_env\Scripts\activate
    
3. **Install the dependencies:**
   ```
   pip install -r requirements.txt

4. **Build docker image:**
   ```
   docker-compose build
   docker-compose up
   docker-compose exec web python manage.py migrate

 