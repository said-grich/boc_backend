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
   ```
2. Create a virtual environment:
   ```
  python -m venv boc_env
  boc_env\Scripts\activate
   ```
3.Install the dependencies:
   ```
   pip install -r requirements.txt

   ```
4.Run the development server

   ```
   python manage.py makemigrations
   python manage.py migrate
   python manage.py runserver

   ```