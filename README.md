# Django Project Setup Guide

This guide provides step-by-step instructions for setting up and running a Django project with Tailwind CSS v4 and PostgreSQL on your machine.

## Table of Contents
- [Creating a New Django Project](#creating-a-new-django-project)
- [Database Configuration](#database-configuration)
- [Static Files Configuration](#static-files-configuration)
- [File Uploads (Images)](#file-uploads-images)
- [Installing Tailwind CSS v4](#installing-tailwind-css-v4)
- [Database Migration Commands](#database-migration-commands)
- [Cloning an Existing Project](#cloning-an-existing-project)
- [Common Issues and Solutions](#common-issues-and-solutions)
- [Additional Commands](#additional-commands)
- [Generating Requirements File](#generating-requirements-file)

## Creating a New Django Project

1. Create a virtual environment:
   ```bash
   python -m venv <env_name>
   ```

2. Activate the virtual environment:
   - Windows:
     ```bash
     <env_name>\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source <env_name>/bin/activate
     ```

3. Install Django and required packages:
   ```bash
   pip install Django
   ```

4. Create a new Django project:
   ```bash
   django-admin startproject <project_name> .
   ```
   Note: The dot (.) at the end creates the project in the current directory.

5. Create a new Django app:
	 ```bash
   django-admin startapp <app_name>
   ```

6. Add your app to the project settings:
   Open `<project_name>/settings.py` and add your app to `INSTALLED_APPS`:
   ```python
   INSTALLED_APPS = [
       'django.contrib.admin',
       'django.contrib.auth',
       # ... other default apps
       '<app_name>',  # Add your app here
   ]
   ```

## Database Configuration
1. Open the terminal and run the command (make sure virtual environment is activated)
	```bash
	pip install psycopg2-binary
   ```
2. Configure PostgreSQL in your Django project:
   Open `<project_name>/settings.py` and replace the default database settings with:

   ```python
   # Database: PostgreSQL
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': '<database_name>',
           'USER': 'postgres',
           'PASSWORD': '<database_password>',
           'HOST': 'localhost',
           'PORT': '5432'
       }
   }
   ```

3. For better security, consider using environment variables with python-decouple.
	```bash
   pip install python-decouple
   ```
   
   Create a `.env` file in your project root:
   ```
   DB_NAME=<database_name>
   DB_USER=postgres
   DB_PASSWORD=<database_password>
   DB_HOST=localhost
   DB_PORT=5432
   ```

   Then update your settings.py:
   ```python
   from decouple import config

   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': config('DB_NAME'),
           'USER': config('DB_USER'),
           'PASSWORD': config('DB_PASSWORD'),
           'HOST': config('DB_HOST'),
           'PORT': config('DB_PORT'),
       }
   }
   ```

## Static Files Configuration

1. Configure static files in `settings.py`:
   ```python
   # Static files (CSS, JavaScript, Images)
   STATIC_URL = '/static/'
   STATICFILES_DIRS = [
       BASE_DIR / "static",
   ]
   STATIC_ROOT = BASE_DIR / "staticfiles"
   ```

2. Create the static directory structure:
   ```bash
   mkdir -p static/{css,js,images}
   ```

3. Add static files to your templates:
   ```html
   {% load static %}
   
   <!-- CSS -->
   <link rel="stylesheet" href="{% static 'css/output.css' %}">
   
   <!-- JavaScript -->
   <script src="{% static 'js/main.js' %}"></script>
   
   <!-- Images -->
   <img src="{% static 'images/logo.png' %}" alt="Logo">
   ```

4. Collect static files for production:
   ```bash
   python manage.py collectstatic
   ```

## File Uploads (Images)

1. Configure media files in `settings.py`:
   ```python
   # Media files (User uploads)
   MEDIA_URL = '/media/'
   MEDIA_ROOT = BASE_DIR / 'media'
   ```

2. Update your project's `urls.py` to serve media files during development:
   ```python
   from django.conf import settings
   from django.conf.urls.static import static
   from django.contrib import admin
   from django.urls import path, include

   urlpatterns = [
       path('admin/', admin.site.urls),
       path('', include('app_name.urls')),
       # ... other URL patterns
   ]

   urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
   ```

3. Create a model with an image field:
   ```python
   from django.db import models

   class Profile(models.Model):
       name = models.CharField(max_length=100)
       avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
       
       def __str__(self):
           return self.name
   ```

4. Install Pillow for image processing:
   ```bash
   pip install Pillow
   ```

5. Create and apply migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. Create a form with file upload capability:
   ```python
   # forms.py
   from django import forms
   from .models import Profile

   class ProfileForm(forms.ModelForm):
       class Meta:
           model = Profile
           fields = ['name', 'avatar']
   ```

7. Display and handle file uploads in a view:
   ```python
   # views.py
   from django.shortcuts import render, redirect
   from .forms import ProfileForm
   from .models import Profile

   def profile_create(request):
       if request.method == 'POST':
           form = ProfileForm(request.POST, request.FILES)
           if form.is_valid():
               form.save()
               return redirect('profile_list')
       else:
           form = ProfileForm()
       return render(request, 'app_name/profile_form.html', {'form': form})
   ```

8. Create a template with a file upload form:
   ```html
   {% extends "base.html" %}
   
   {% block content %}
   <div class="container mx-auto">
       <h1>Create Profile</h1>
       <form method="post" enctype="multipart/form-data">
           {% csrf_token %}
           {{ form.as_p }}
           <button type="submit">Save</button>
       </form>
   </div>
   {% endblock %}
   ```

9. Display uploaded images:
   ```html
   <img src="{{ profile.avatar.url }}" alt="{{ profile.name }}">
   ```

## Installing Tailwind CSS v4

1. Install Tailwind CSS and required packages:
   ```bash
   npm install tailwindcss @tailwindcss/postcss postcss
   ```

2. Create a PostCSS configuration file in the root directory:
   ```bash
   # Create file: postcss.config.mjs
   ```

3. Add the following code to `postcss.config.mjs`:
   ```javascript
   export default {
     plugins: {
       "@tailwindcss/postcss": {},
     }
   }
   ```

4. Create or update the CSS input file:
   ```bash
   # Create directory if it doesn't exist
   mkdir -p static/css
   # Create file: static/css/input.css
   ```

5. Add the following code to `static/css/input.css`:
   ```css
   @import "tailwindcss";
   ```

6. Add the following scripts to your `package.json` file (create it if it doesn't exist):
   ```json
   {
     "scripts": {
       "build:tailwind": "npx @tailwindcss/cli -i ./static/css/input.css -o ./static/css/output.css --minify",
       "watch:tailwind": "npx @tailwindcss/cli -i ./static/css/input.css -o ./static/css/output.css --watch"
     }
   }
   ```

7. Include the compiled CSS in your HTML templates:
   ```html
   {% load static %}
   <link rel="stylesheet" href="{% static 'css/output.css' %}">
   ```
   Note: Add `{% load static %}` at the top of your HTML file.

8. Run Tailwind in watch mode during development:
   ```bash
   npm run watch:tailwind
   ```

## Database Migration Commands

After making changes to your models, run these commands:

1. Create migration files:
   ```bash
   python manage.py makemigrations
   ```

2. Apply migrations to the database:
   ```bash
   python manage.py migrate
   ```

## Cloning an Existing Project

1. Clone the repository:
   ```bash
   git clone https://github.com/username/repository-name.git
   cd repository-name
   ```

2. Set up a virtual environment:
   ```bash
   # Create a virtual environment
   python -m venv venv

   # Activate the virtual environment (Windows)
   venv\Scripts\activate
   
   # Activate the virtual environment (macOS/Linux)
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables (if needed):
   ```bash
   # Copy the example environment file
   copy .env.example .env  # Windows
   # cp .env.example .env  # macOS/Linux

   # Edit the environment file with your settings
   ```

5. Set up the database:
   ```bash
   # Run migrations
   python manage.py migrate

   # Create a superuser for the admin panel
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

   The site should now be available at http://127.0.0.1:8000/

7. Accessing the admin panel:
   
   After creating a superuser, you can access the admin panel at:
   http://127.0.0.1:8000/admin/

## Common Issues and Solutions

### Package Installation Problems

If you encounter issues installing packages:

```bash
# Try installing packages one by one
pip install django
pip install psycopg2-binary
pip install python-decouple
pip install [package_name]
```

### Database Connection Issues

If using PostgreSQL or MySQL, ensure:
- The database service is running
- PostgreSQL is properly installed on your system
- Your connection settings in settings.py or .env file are correct
- The specified database exists (you may need to create it first)

```bash
# Example for creating a PostgreSQL database
# Connect to PostgreSQL
psql -U postgres

# Create the database
CREATE DATABASE django_todo_db;

# Exit
\q
```

### Missing Static Files

If static files aren't loading properly:

```bash
# Collect static files
python manage.py collectstatic
```

### File Upload Issues

If you're having issues with file uploads:

1. Check MEDIA_ROOT and MEDIA_URL settings
2. Ensure the form has `enctype="multipart/form-data"`
3. Verify that Pillow is installed (`pip install Pillow`)
4. Ensure the upload directory exists and is writable
5. Check file size limits in your Django settings:

```python
# Add to settings.py to increase upload limit
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
```

## Additional Commands

```bash
# Run tests
python manage.py test

# Create a new Django app
python manage.py startapp [app_name]

# Generate requirements.txt file
pip freeze > requirements.txt

# Install dependencies:
pip install -r requirements.txt
```

## Generating Requirements File

To create a requirements.txt file that lists all the Python packages installed in your virtual environment:

```bash
# Make sure your virtual environment is activated, then run:
pip freeze > requirements.txt
```

This file is essential when sharing your project with others or deploying it to a production server. It allows others to install the exact same package versions you used.

Be sure to include the following essential packages in your requirements.txt:
```
Django==4.2.x  # Or your current version
psycopg2-binary==2.9.x  # For PostgreSQL support
python-decouple==3.8  # For environment variables
Pillow==10.x.x  # For image processing
```

## Deactivating the Virtual Environment

When you're done working on the project:

```bash
deactivate
```

---

<div align="center">
<h1> Dabananda Mitra </h1>
</div>

<div align="center">
  <img src="https://res.cloudinary.com/djz3p8sux/image/upload/v1742125099/dabananda_mitra_formal_Small_1x1_o8uxit.png" width="250" height="250" style="border-radius: 50%">
</div>

<h3 align="center">Software Engineer | Problem Solver | Open Source Enthusiast</h3>

---

### 🌐 Connect with Me

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/dabananda) [![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/dabananda) [![Twitter](https://img.shields.io/badge/X-000000?style=for-the-badge&logo=x&logoColor=white)](https://x.com/dabanandamitra) [![Facebook](https://img.shields.io/badge/Facebook-1877F2?style=for-the-badge&logo=facebook&logoColor=white)](https://www.facebook.om/imdmitra/) [![WhatsApp](https://img.shields.io/badge/WhatsApp-25D366?style=for-the-badge&logo=whatsapp&logoColor=white)](https://wa.me/8801304080014) [![Discord](https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discordapp.com/users/dabanandamitra)

---

### 💻 Online Judge Profiles

[![LeetCode](https://img.shields.io/badge/-LeetCode-FFA116?style=for-the-badge)](https://leetcode.com/u/dabananda/) [![Codeforces](https://img.shields.io/badge/-Codeforces-1F8ACB?style=for-the-badge)](https://codeforces.com/profile/dabananda) [![CodeChef](https://img.shields.io/badge/-CodeChef-5B4638?style=for-the-badge)](https://www.codechef.com/users/dabananda) [![HackerRank](https://img.shields.io/badge/-HackerRank-00EA64?style=for-the-badge)](https://www.hackerrank.com/profile/dabananda) [![CodingNinjas](https://img.shields.io/badge/-Coding_Ninjas-FFA500?style=for-the-badge)](https://www.naukri.com/code360/profile/48a35475-0af2-4d4e-8f26-2d793b64843a) [![UVa](https://img.shields.io/badge/-UVa-00B388?style=for-the-badge)](https://uhunt.onlinejudge.org/id/1167157) [![Beecrowd](https://img.shields.io/badge/-Beecrowd-009688?style=for-the-badge)](https://judge.beecrowd.com/en/profile/467832) [![Vjudge](https://img.shields.io/badge/-Vjudge-8A2BE2?style=for-the-badge)](https://vjudge.net/user/dabanandamitra)