"""
Load testing script for Base10 Backend using Locust.
Tests sync/push endpoint with 1000+ concurrent users.

Run with:
    locust -f locustfile.py --host=http://localhost:8000
    
Then open http://localhost:8089 to configure test parameters.
"""
from locust import HttpUser, task, between, events
from datetime import datetime
import random
import string


class Base10User(HttpUser):
    """
    Simulates a student user syncing offline attempts to the backend.
    """
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """Called when a simulated user starts. Register/login to get auth token."""
        # Generate unique user credentials
        user_id = ''.join(random.choices(string.digits, k=10))
        self.phone_number = f"+2347{user_id}"
        self.email = f"loadtest{user_id}@test.com"
        self.password = "TestPass123!"
        
        # Register user
        register_response = self.client.post("/api/v1/auth/register", json={
            "phone_number": self.phone_number,
            "email": self.email,
            "password": self.password,
            "full_name": f"Load Test User {user_id}",
            "country_code": "NG"
        }, name="/auth/register")
        
        if register_response.status_code in [200, 201]:
            # Auto-verify OTP (if endpoint exists) or login directly
            login_response = self.client.post("/api/v1/auth/login", data={
                "username": self.phone_number,
                "password": self.password
            }, name="/auth/login")
            
            if login_response.status_code == 200:
                data = login_response.json()
                self.token = data.get("access_token")
                self.headers = {"Authorization": f"Bearer {self.token}"}
                self.user_id = data.get("user", {}).get("id")
            else:
                print(f"❌ Login failed: {login_response.status_code}")
                self.token = None
                self.headers = {}
        else:
            # User might already exist, try login
            login_response = self.client.post("/api/v1/auth/login", data={
                "username": self.phone_number,
                "password": self.password
            }, name="/auth/login")
            
            if login_response.status_code == 200:
                data = login_response.json()
                self.token = data.get("access_token")
                self.headers = {"Authorization": f"Bearer {self.token}"}
                self.user_id = data.get("user", {}).get("id")
            else:
                print(f"❌ Registration and login failed for {self.phone_number}")
                self.token = None
                self.headers = {}
        
        # Cache some question IDs for sync
        if hasattr(self, 'token') and self.token:
            questions_response = self.client.get(
                "/api/v1/questions/random?limit=10",
                headers=self.headers,
                name="/questions/random"
            )
            if questions_response.status_code == 200:
                self.questions = questions_response.json()
            else:
                self.questions = []
    
    @task(5)
    def sync_attempts(self):
        """Sync offline attempts - most common operation (5x weight)."""
        if not hasattr(self, 'token') or not self.token:
            return
        
        if not hasattr(self, 'questions') or len(self.questions) == 0:
            return
        
        # Generate 1-5 attempts to sync
        num_attempts = random.randint(1, 5)
        attempts = []
        
        for _ in range(num_attempts):
            question = random.choice(self.questions)
            is_correct = random.random() > 0.4  # 60% accuracy
            
            # Varied psychometric patterns
            pattern = random.choice(['normal', 'guesser', 'struggler'])
            
            if pattern == 'guesser':
                time_taken_ms = random.randint(800, 1800)  # <2s
                confidence = random.randint(1, 2)
            elif pattern == 'struggler':
                time_taken_ms = random.randint(62000, 120000)  # >60s
                confidence = random.randint(1, 3)
            else:
                time_taken_ms = random.randint(10000, 45000)  # 10-45s
                confidence = random.randint(2, 4)
            
            attempts.append({
                "question_id": question["id"],
                "is_correct": is_correct,
                "selected_option": random.randint(0, 3),
                "attempted_at": datetime.utcnow().isoformat(),
                "time_taken_ms": time_taken_ms,
                "confidence_level": confidence,
                "network_type": random.choice(["wifi", "4g", "3g", "2g", "offline"]),
                "app_version": random.choice(["1.0.0", "0.9.9", "0.9.8"])
            })
        
        # Push sync
        device_id = f"device_{self.user_id}"
        sync_data = {
            "attempts": attempts,
            "device_id": device_id
        }
        
        self.client.post(
            "/api/v1/sync/push",
            json=sync_data,
            headers=self.headers,
            name="/sync/push"
        )
    
    @task(2)
    def get_sync_stats(self):
        """Get sync statistics - less frequent (2x weight)."""
        if not hasattr(self, 'token') or not self.token:
            return
        
        self.client.get(
            "/api/v1/sync/stats",
            headers=self.headers,
            name="/sync/stats"
        )
    
    @task(1)
    def get_random_questions(self):
        """Fetch random questions - occasional operation (1x weight)."""
        if not hasattr(self, 'token') or not self.token:
            return
        
        limit = random.choice([5, 10, 20])
        self.client.get(
            f"/api/v1/questions/random?limit={limit}",
            headers=self.headers,
            name="/questions/random"
        )
    
    @task(1)
    def get_profile(self):
        """Check user profile - occasional operation (1x weight)."""
        if not hasattr(self, 'token') or not self.token:
            return
        
        self.client.get(
            "/api/v1/profile/me",
            headers=self.headers,
            name="/profile/me"
        )


class TeacherUser(HttpUser):
    """
    Simulates a teacher user accessing analytics.
    """
    wait_time = between(5, 10)  # Teachers check less frequently
    
    def on_start(self):
        """Register/login as teacher."""
        user_id = ''.join(random.choices(string.digits, k=10))
        self.phone_number = f"+2348{user_id}"
        self.email = f"teacher{user_id}@test.com"
        self.password = "TeacherPass123!"
        
        # Register as teacher
        register_response = self.client.post("/api/v1/auth/register", json={
            "phone_number": self.phone_number,
            "email": self.email,
            "password": self.password,
            "full_name": f"Teacher Load Test {user_id}",
            "country_code": "NG"
        }, name="/auth/register")
        
        if register_response.status_code in [200, 201]:
            login_response = self.client.post("/api/v1/auth/login", data={
                "username": self.phone_number,
                "password": self.password
            }, name="/auth/login")
            
            if login_response.status_code == 200:
                data = login_response.json()
                self.token = data.get("access_token")
                self.headers = {"Authorization": f"Bearer {self.token}"}
                
                # Create a test classroom
                classroom_response = self.client.post(
                    "/api/v1/teacher/classrooms",
                    json={
                        "name": f"Load Test Class {user_id}",
                        "description": "Testing classroom for load tests"
                    },
                    headers=self.headers,
                    name="/teacher/classrooms [POST]"
                )
                
                if classroom_response.status_code == 200:
                    self.classroom_id = classroom_response.json()["id"]
                else:
                    self.classroom_id = None
            else:
                self.token = None
                self.headers = {}
        else:
            self.token = None
            self.headers = {}
    
    @task(3)
    def get_analytics(self):
        """Get classroom analytics - primary teacher operation."""
        if not hasattr(self, 'token') or not self.token:
            return
        
        if not hasattr(self, 'classroom_id') or not self.classroom_id:
            return
        
        self.client.get(
            f"/api/v1/teacher/analytics/{self.classroom_id}",
            headers=self.headers,
            name="/teacher/analytics/{id}"
        )
    
    @task(1)
    def list_classrooms(self):
        """List teacher's classrooms."""
        if not hasattr(self, 'token') or not self.token:
            return
        
        self.client.get(
            "/api/v1/teacher/classrooms",
            headers=self.headers,
            name="/teacher/classrooms [GET]"
        )


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when the test starts."""
    print("🚀 Starting Base10 load test...")
    print(f"   Target host: {environment.host}")
    print("   Simulating student sync operations and teacher analytics")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when the test stops."""
    print("\n📊 Load test completed!")
    print(f"   Total requests: {environment.stats.total.num_requests}")
    print(f"   Failed requests: {environment.stats.total.num_failures}")
    if environment.stats.total.num_requests > 0:
        failure_rate = (environment.stats.total.num_failures / environment.stats.total.num_requests) * 100
        print(f"   Failure rate: {failure_rate:.2f}%")
        print(f"   Average response time: {environment.stats.total.avg_response_time:.0f}ms")
        print(f"   95th percentile: {environment.stats.total.get_response_time_percentile(0.95):.0f}ms")
