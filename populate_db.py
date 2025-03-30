import os
import django
from faker import Faker
import random
from tasks.models import Project, Task, TaskDetail
from users.models import CustomUser  # Make sure to import the CustomUser model

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'task_management.settings')
django.setup()

# Function to populate the database
def populate_db():
    # Initialize Faker
    fake = Faker()

    # Create Projects
    projects = [Project.objects.create(
        name=fake.bs().capitalize(),
        description=fake.paragraph(),
        start_date=fake.date_this_year()
    ) for _ in range(5)]
    print(f"Created {len(projects)} projects.")

    # Create Custom Users (Employees)
    users = [CustomUser.objects.create(
        username=fake.user_name(),
        email=fake.email(),
        password=fake.password(),  # You might want to hash this password in a real scenario
        profile_image='profile_images/default.png',  # Placeholder image
        bio=fake.sentence()
    ) for _ in range(10)]
    print(f"Created {len(users)} users.")

    # Create Tasks
    tasks = []
    for _ in range(20):
        task = Task.objects.create(
            project=random.choice(projects),
            title=fake.sentence(),
            description=fake.paragraph(),
            due_date=fake.date_this_year(),
            status=random.choice(['PENDING', 'IN_PROGRESS', 'COMPLETED']),
        )
        task.assigned_to.set(random.sample(users, random.randint(1, 3)))
        tasks.append(task)
    print(f"Created {len(tasks)} tasks.")

    # Create Task Details
    for task in tasks:
        TaskDetail.objects.create(
            task=task,
            asset='tasks_asset/default_img.jpg',  # Placeholder image
            priority=random.choice(['H', 'M', 'L']),
            notes=fake.paragraph()
        )
    print("Populated TaskDetails for all tasks.")
    print("Database populated successfully!")

if __name__ == "__main__":
    populate_db()