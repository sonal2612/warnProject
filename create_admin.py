import os
from app import app, db, User, bcrypt

with app.app_context():
    username = input("Enter admin username: ")
    email = input("Enter admin email: ")
    password = input("Enter admin password: ")
    
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        print(f"User '{username}' already exists!")
    else:
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        admin_user = User(username=username, email=email, password_hash=hashed_password, role='admin')
        db.session.add(admin_user)
        db.session.commit()
        print(f"Admin user '{username}' created successfully!")
