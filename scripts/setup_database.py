#!/usr/bin/env python3
"""
Simple database setup script for DocManager demo.
Creates database and populates with Lokesh Dagdiya data.
Works on both Windows and macOS from any working directory.
"""

import os
import sys
from pathlib import Path

# Get the absolute path to the project root (cross-platform)
# This script is in scripts/, so go up one level
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent
backend_dir = project_root / 'ca_desktop' / 'backend'

# Add project root and backend to Python path
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(backend_dir))

# Change to project root for database file
os.chdir(str(project_root))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import using full module path (works cross-platform)
try:
    from ca_desktop.backend.src.database import Base
    from ca_desktop.backend.src.models import User, CAProfile, Service, Testimonial, Client
except ImportError:
    from src.database import Base
    from src.models import User, CAProfile, Service, Testimonial, Client

import bcrypt

def get_password_hash(password: str) -> str:
    """Hash password using bcrypt directly."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Create engine directly - database in project root
DATABASE_URL = "sqlite:///ca_desktop.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def setup_demo_data():
    """Setup complete demo data for testing."""
    
    print("🚀 Setting up DocManager Demo Data...")
    print("=" * 60)
    
    # Create all tables
    print("\n📦 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")
    
    db = SessionLocal()
    
    try:
        # Check if CA user already exists
        existing_ca = db.query(User).filter(User.username == "lokesh").first()
        if existing_ca:
            print("\n⚠️  CA user 'lokesh' already exists. Skipping user creation.")
            ca_user = existing_ca
        else:
            # Create CA User
            print("\n👤 Creating CA User: Lokesh Dagdiya")
            ca_user = User(
                username="lokesh",
                email="lokesh@dagdiyaassociates.com",
                password_hash=get_password_hash("lokesh"),
                display_name="CA Lokesh Dagdiya",
                slug="lokesh-dagdiya",
            )
            db.add(ca_user)
            db.commit()
            db.refresh(ca_user)
            print(f"✅ CA User created - Username: lokesh, Password: lokesh")
        
        # Create/Update CA Profile
        existing_profile = db.query(CAProfile).filter(CAProfile.ca_id == ca_user.id).first()
        if existing_profile:
            print("\n📝 Updating CA Profile...")
            existing_profile.firm_name = "Lokesh Dagdiya & Associates"
            existing_profile.professional_bio = """CA Lokesh Dagdiya is a Fellow Chartered Accountant from ICAI with DISA and certifications in Concurrent Audit and Forensic Audit. He specializes in GST compliances, consultancy and litigation, along with comprehensive bank audits including statutory, forensic, concurrent audits, and due diligence reviews. Currently serving as Treasurer of Nanded Branch of WIRC of ICAI."""
            existing_profile.address = "Vazirabad, Nanded, Nanded-Waghala, Maharashtra 431601"
            existing_profile.phone_number = "+91 98901 54945"
            existing_profile.email = "lokesh@dagdiyaassociates.com"
            ca_profile = existing_profile
        else:
            print("\n📝 Creating CA Profile...")
            ca_profile = CAProfile(
                ca_id=ca_user.id,
                firm_name="Lokesh Dagdiya & Associates",
                professional_bio="""CA Lokesh Dagdiya is a Fellow Chartered Accountant from ICAI with DISA and certifications in Concurrent Audit and Forensic Audit. He specializes in GST compliances, consultancy and litigation, along with comprehensive bank audits including statutory, forensic, concurrent audits, and due diligence reviews. Currently serving as Treasurer of Nanded Branch of WIRC of ICAI.""",
                address="Vazirabad, Nanded, Nanded-Waghala, Maharashtra 431601",
                phone_number="+91 98901 54945",
                email="lokesh@dagdiyaassociates.com",
            )
            db.add(ca_profile)
        
        db.commit()
        print("✅ CA Profile created/updated")
        
        # Create Services
        print("\n🛠️  Creating Services...")
        db.query(Service).filter(Service.ca_id == ca_user.id).delete()
        
        services = [
            {"name": "GST Compliances & Litigation", "description": "Comprehensive GST services including compliances, consultancy, litigation support, and representation before authorities.", "order_index": 1},
            {"name": "Bank Audits (Specialized)", "description": "Statutory, forensic, concurrent audits, due diligence reviews, and stock & debtor audits for banking sector.", "order_index": 2},
            {"name": "Forensic Audit & Fraud Detection", "description": "Certified forensic accounting, fraud investigation, and financial irregularity detection services.", "order_index": 3},
            {"name": "Information System Audit", "description": "DISA-certified IT system audits, cybersecurity assessments, and IT compliance reviews.", "order_index": 4},
        ]
        
        for svc in services:
            service = Service(ca_id=ca_user.id, name=svc["name"], description=svc["description"], is_active=True, order_index=svc["order_index"])
            db.add(service)
        
        db.commit()
        print(f"✅ {len(services)} services created")
        
        # Create Testimonials
        print("\n⭐ Creating Testimonials...")
        db.query(Testimonial).filter(Testimonial.ca_id == ca_user.id).delete()
        
        testimonials = [
            {"client_name": "Amit Sharma", "text": "Lokesh has been handling our accounts for the past 5 years. His attention to detail and proactive tax planning has saved us lakhs in taxes. Highly recommended!", "rating": 5},
            {"client_name": "Priya Patel", "text": "As a startup founder, I needed someone who understood both business and compliance. Lokesh provided invaluable guidance during our growth phase. Professional and reliable!", "rating": 5},
            {"client_name": "Rahul Mehta", "text": "The audit and compliance services provided by Lokesh Dagdiya & Associates are top-notch. They handle all our complex real estate transactions with ease.", "rating": 5},
        ]
        
        for test in testimonials:
            testimonial = Testimonial(ca_id=ca_user.id, client_name=test["client_name"], text=test["text"], rating=test["rating"], is_active=True)
            db.add(testimonial)
        
        db.commit()
        print(f"✅ {len(testimonials)} testimonials created")
        
        # Create Sample Clients
        print("\n👥 Creating Sample Clients...")
        
        sample_clients = [
            {"phone": "9876543210", "name": "Amit Sharma", "email": "amit@example.com"},
            {"phone": "9876543211", "name": "Priya Patel", "email": "priya@example.com"},
            {"phone": "9876543212", "name": "Rahul Mehta", "email": "rahul@example.com"},
            {"phone": "9876543213", "name": "Sneha Desai", "email": "sneha@example.com"},
            {"phone": "9876543214", "name": "Vikram Singh", "email": "vikram@example.com"},
        ]
        
        for client_data in sample_clients:
            existing_client = db.query(Client).filter(Client.phone_number == client_data["phone"]).first()
            if not existing_client:
                client = Client(phone_number=client_data["phone"], name=client_data["name"], email=client_data["email"], password_hash=get_password_hash("client123"), is_active=True)
                db.add(client)
        
        db.commit()
        print(f"✅ {len(sample_clients)} sample clients created (password: client123)")
        
        print("\n" + "=" * 60)
        print("🎉 Demo Data Setup Complete!")
        print("=" * 60)
        print("\n📋 Login Credentials:")
        print("   CA Dashboard:")
        print(f"   - URL: http://localhost:5173/ca/login")
        print(f"   - Username: lokesh")
        print(f"   - Password: lokesh")
        print()
        print("   Client Portal:")
        print(f"   - URL: http://localhost:5173/ca-lokesh-dagdiya/login")
        print(f"   - Username: 9876543210 (or any client phone)")
        print(f"   - Password: client123")
        print()
        print("🌐 Public Website:")
        print(f"   - URL: http://localhost:5173/ca-lokesh-dagdiya")
        print()
        print("🚀 Next Steps:")
        print("   1. Start backend: cd ca_desktop/backend && uvicorn src.main:app --reload --port 8443")
        print("   2. Start frontend: cd ca_desktop/frontend && npm run dev")
        print("   3. Open browser and test!")
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    setup_demo_data()
