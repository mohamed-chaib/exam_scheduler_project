from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from . import models
from passlib.context import CryptContext
import random
import string

# Create tables if they don't exist (ensure User table is created)
models.Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def get_random_string(length=8):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))

def get_password_hash(password):
    return pwd_context.hash(password)

def seed_users():
    db = SessionLocal()
    
    users_to_create = []
    
    # 1. Dean and Vice-Dean
    users_to_create.append({
        "email": "dean@university.edu",
        "role": "dean",
        "dept_id": None
    })
    
    # 2. Exam Administrator
    users_to_create.append({
        "email": "admin@university.edu",
        "role": "admin",
        "dept_id": None
    })
    
    # 3. Heads of Departments
    departments = db.query(models.Departement).all()
    for dept in departments:
        # Create email based on dept name
        sanitized_name = dept.nom.lower().replace(" ", "_")
        email = f"head_{sanitized_name}@university.edu"
        
        users_to_create.append({
            "email": email,
            "role": "head_of_dept",
            "dept_id": dept.id
        })
        
    created_credentials = []

    try:
        # Clear existing users to avoid duplicates (optional, or check existence)
        # For safety, let's check existence first
        
        for user_data in users_to_create:
            existing_user = db.query(models.User).filter(models.User.email == user_data["email"]).first()
            
            password = get_random_string(10)
            hashed = get_password_hash(password)
            
            if not existing_user:
                new_user = models.User(
                    email=user_data["email"],
                    hashed_password=hashed,
                    role=user_data["role"],
                    department_id=user_data["dept_id"]
                )
                db.add(new_user)
                created_credentials.append(f"Role: {user_data['role']} | Email: {user_data['email']} | Password: {password}")
            else:
                # If user exists, we might want to update password, or just skip
                # Let's update password to ensure we have the credentials
                existing_user.hashed_password = hashed
                created_credentials.append(f"Role: {user_data['role']} | Email: {user_data['email']} | Password: {password} (Updated)")
        
        db.commit()
        
        # Write credentials to file
        output_file = "../generated_credentials.txt"
        with open(output_file, "w") as f:
            f.write("=== EXAM SCHEDULER CREDENTIALS ===\n\n")
            for line in created_credentials:
                f.write(line + "\n")
                
        print(f"✅ Successfully seeded {len(created_credentials)} users.")
        print(f"📂 Credentials saved to {output_file}")
        
    except Exception as e:
        print(f"Error seeding users: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_users()
