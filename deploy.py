import os
from pythonanywhere.project import Project

username = os.environ['PA_USERNAME']
token = os.environ['PA_API_TOKEN']

project = Project(username, token)

# Update source code
project.update_from_github(
    'https://github.com/OnomeAkpobaro/payment_API.git',
    branch='main'
)

# Install requirements
project.install_requirements('requirements.txt')

# Collect static files
project.run_command('python manage.py collectstatic --noinput')

# Apply migrations
project.run_command('python manage.py migrate --noinput')

# Reload web app
project.reload_web_app()