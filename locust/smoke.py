from locust import HttpUser, between, task


class PublicPagesUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def load_public_page(self):
        self.client.get("/")

    @task
    def load_services(self):
        self.client.get("/servicios")

    @task
    def load_promotions(self):
        self.client.get("/promociones")

    @task
    def load_about_page(self):
        self.client.get("/quienesomos")
