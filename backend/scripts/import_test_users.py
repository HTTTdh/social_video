import sys
from pathlib import Path

# Thêm backend vào sys.path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

import bcrypt
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.roles_models import Role
from app.models.auth_models import User


def hash_password(password: str) -> str:
    """Hash password với bcrypt"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def create_test_data():
    """Tạo dữ liệu test cơ bản cho login"""
    db = SessionLocal()
    
    try:
        print("1. Tạo roles cơ bản...")
        # Kiểm tra và tạo roles nếu chưa có
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        if not admin_role:
            admin_role = Role(name="admin", permissions={"all": True})
            db.add(admin_role)
            print("  ✓ Đã tạo role admin")
            
        staff_role = db.query(Role).filter(Role.name == "staff").first()
        if not staff_role:
            staff_role = Role(name="staff", permissions={"posts": True, "channels": True})
            db.add(staff_role)
            print("  ✓ Đã tạo role staff")
            
        user_role = db.query(Role).filter(Role.name == "user").first()
        if not user_role:
            user_role = Role(name="user", permissions={"view": True})
            db.add(user_role)
            print("  ✓ Đã tạo role user")
        
        db.commit()
        
        print("\n2. Tạo users test...")
        # Tạo admin user nếu chưa có
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                email="admin@example.com",
                full_name="Admin User",
                hashed_password=hash_password("admin123"),
                is_active=True
            )
            db.add(admin)
            print("  ✓ Đã tạo user admin (admin@example.com / admin123)")
        
        # Tạo staff user nếu chưa có
        staff = db.query(User).filter(User.username == "staff").first()
        if not staff:
            staff = User(
                username="staff",
                email="staff@example.com",
                full_name="Staff User",
                hashed_password=hash_password("staff123"),
                is_active=True
            )
            db.add(staff)
            print("  ✓ Đã tạo user staff (staff@example.com / staff123)")
        
        # Tạo regular user nếu chưa có
        regular = db.query(User).filter(User.username == "user").first()
        if not regular:
            regular = User(
                username="user",
                email="user@example.com",
                full_name="Regular User",
                hashed_password=hash_password("user123"),
                is_active=True
            )
            db.add(regular)
            print("  ✓ Đã tạo user thường (user@example.com / user123)")
        
        db.commit()
        
        print("\n3. Gán roles cho users...")
        # Reload users để đảm bảo có ID
        admin = db.query(User).filter(User.username == "admin").first()
        staff = db.query(User).filter(User.username == "staff").first()
        regular = db.query(User).filter(User.username == "user").first()
        
        # Reload roles
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        staff_role = db.query(Role).filter(Role.name == "staff").first()
        user_role = db.query(Role).filter(Role.name == "user").first()
        
        # Gán roles
        if admin and admin_role not in admin.roles:
            admin.roles.append(admin_role)
            print(f"  ✓ Đã gán role admin cho user {admin.username}")
            
        if staff and staff_role not in staff.roles:
            staff.roles.append(staff_role)
            print(f"  ✓ Đã gán role staff cho user {staff.username}")
            
        if regular and user_role not in regular.roles:
            regular.roles.append(user_role)
            print(f"  ✓ Đã gán role user cho user {regular.username}")
        
        db.commit()
        
        print("\n✅ Hoàn tất! Đã tạo dữ liệu test cho login")
        print("\nThông tin đăng nhập:")
        print("  1. Admin: admin@example.com / admin123")
        print("  2. Staff: staff@example.com / staff123")
        print("  3. User:  user@example.com / user123")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ LỖI: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    create_test_data()