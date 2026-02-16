import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backapi.settings')
django.setup()

from accounts.models import User

def create_admin_user():
    username = 'admin'
    email = 'admin@example.com'
    password = 'AdminPassword2026!'
    
    if not User.objects.filter(username=username).exists():
        print(f"Creating superuser {username}...")
        User.objects.create_superuser(username=username, email=email, password=password)
        print("Superuser created successfully.")
    else:
        print(f"User {username} already exists.")
        u = User.objects.get(username=username)
        if not u.is_superuser:
            print(f"User {username} is not a superuser. Promoting...")
            u.is_superuser = True
            u.is_staff = True
            u.save()
            print("User promoted to superuser.")
        
        print("Updating password...")
        u.set_password(password)
        u.save()
        print("Password updated successfully.")

    print("\n--------------------------------------------------")
    print(f"Admin Username: {username}")
    print(f"Admin Password: {password}")
    print("--------------------------------------------------")

if __name__ == "__main__":
    create_admin_user()
