from locust import HttpUser, task, between

class TestUser(HttpUser):
    host = "http://localhost:5000"
    wait_time = between(1, 3)

    @task
    def view_accommodations(self):
        self.client.get("/accommodations/")