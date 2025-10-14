import time
from locust import HttpUser, task, between

class AppUser(HttpUser):
    wait_times = between(1, 5)

    @task(3)
    def create_account(self):
        self.client.get("/api/accounting/orchestrator/create-account")

    @task(1)
    def block_transaction(self):
        self.client.post("/api/risk/orchestrator/block-transaction")

    def on_start(self):
        pass
