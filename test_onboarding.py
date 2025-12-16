#!/usr/bin/env python3
"""
Test user registration and email onboarding flow
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_student_registration():
    """Test student registration with email onboarding"""
    print("=" * 70)
    print("📝 Testing Student Registration & Onboarding")
    print("=" * 70)
    
    # Get email from user
    email = input("\nEnter your email to test registration: ").strip()
    
    if not email or '@' not in email:
        print("❌ Invalid email address")
        return
    
    print(f"\n1️⃣ Registering new student account...")
    
    registration_data = {
        "email": email,
        "password": "TestPass123!",
        "full_name": "Test Student",
        "role": "student"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=registration_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            data = response.json()
            print("✅ Registration successful!")
            print(f"   User ID: {data['user']['id']}")
            print(f"   Email: {data['user']['email']}")
            print(f"   Role: {data['user']['role']}")
            print(f"   Verified: {data['user']['is_verified']}")
            print(f"   Token: {data['access_token'][:20]}...")
            
            token = data['access_token']
            
            # Wait a moment for background task to send email
            print(f"\n2️⃣ Sending welcome email in background...")
            time.sleep(2)
            
            print(f"\n✅ Check your email inbox at: {email}")
            print(f"   Subject: 'Welcome to Base10, Test Student! 🎉'")
            print(f"   You should receive:")
            print(f"   • Beautiful HTML welcome email")
            print(f"   • Email verification link")
            print(f"   • Student onboarding steps")
            
            # Optional: Test resend verification
            test_resend = input(f"\n3️⃣ Do you want to test resend verification? (y/n): ").strip().lower()
            
            if test_resend == 'y':
                resend_response = requests.post(
                    f"{BASE_URL}/auth/resend-verification",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json"
                    }
                )
                
                if resend_response.status_code == 200:
                    print("✅ Verification reminder sent!")
                    print(f"   Check email again for verification reminder")
                else:
                    print(f"⚠️  Resend response: {resend_response.status_code}")
                    print(f"   {resend_response.text}")
            else:
                print("⏭️  Skipped resend verification test")
            
            print("\n" + "=" * 70)
            print("🎉 Registration Test Complete!")
            print("=" * 70)
            print("\n📋 Next Steps:")
            print("1. Check your email inbox (and spam folder)")
            print("2. Click the 'Verify Email' button in the email")
            print("3. You should receive a post-verification guidance email")
            print("\n💡 To verify programmatically, you need the token from the email link")
            
            return token
            
        elif response.status_code == 400:
            error = response.json()
            print(f"⚠️  Registration failed: {error.get('detail', 'Unknown error')}")
            
            if "already registered" in error.get('detail', '').lower():
                print(f"\n💡 This email is already registered. Try:")
                print(f"   • Use a different email")
                print(f"   • Or test login instead")
                
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"   {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server!")
        print("   Make sure the server is running: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Error: {e}")


def test_teacher_registration():
    """Test teacher registration with classroom onboarding"""
    print("\n" + "=" * 70)
    print("👨‍🏫 Testing Teacher Registration & Onboarding")
    print("=" * 70)
    
    email = input("\nEnter teacher email to test: ").strip()
    
    registration_data = {
        "email": email,
        "password": "TeacherPass123!",
        "full_name": "Test Teacher",
        "role": "teacher"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=registration_data
        )
        
        if response.status_code == 201:
            data = response.json()
            print("✅ Teacher registration successful!")
            print(f"   Check {email} for:")
            print(f"   • Welcome email with classroom setup guide")
            print(f"   • 3-step teacher onboarding")
            print(f"   • Instructions for creating first classroom")
            
        else:
            print(f"⚠️  Status: {response.status_code}")
            print(f"   {response.json()}")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def test_parent_registration():
    """Test parent registration with child linking onboarding"""
    print("\n" + "=" * 70)
    print("👨‍👩‍👧 Testing Parent Registration & Onboarding")
    print("=" * 70)
    
    email = input("\nEnter parent email to test: ").strip()
    
    registration_data = {
        "email": email,
        "password": "ParentPass123!",
        "full_name": "Test Parent",
        "role": "parent"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=registration_data
        )
        
        if response.status_code == 201:
            data = response.json()
            print("✅ Parent registration successful!")
            print(f"   Check {email} for:")
            print(f"   • Welcome email with monitoring guide")
            print(f"   • Instructions for linking child account")
            print(f"   • Weekly progress report setup")
            
        else:
            print(f"⚠️  Status: {response.status_code}")
            print(f"   {response.json()}")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    print("\n🚀 Base10 Email Onboarding Flow Test")
    print("=" * 70)
    print("\nThis will test the complete email onboarding flow:")
    print("• User registration")
    print("• Welcome email (role-specific)")
    print("• Email verification")
    print("• Post-verification guidance")
    print("\n" + "=" * 70)
    
    print("\nChoose a test:")
    print("1. Student registration (recommended)")
    print("2. Teacher registration")
    print("3. Parent registration")
    print("4. Test all roles")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        test_student_registration()
    elif choice == "2":
        test_teacher_registration()
    elif choice == "3":
        test_parent_registration()
    elif choice == "4":
        test_student_registration()
        test_teacher_registration()
        test_parent_registration()
    else:
        print("Invalid choice")
    
    print("\n✅ Testing complete!")
    print("\n📧 Remember to check your email inbox (and spam folder)!")


if __name__ == "__main__":
    main()
