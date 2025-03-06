from locust import HttpUser, task, between
import random

class WebsiteUser(HttpUser):
    wait_time = between(1, 5)  # Simulerar realistisk användarbeteende

    def on_start(self):
        """Körs när en ny testanvändare startar – försöker logga in eller registrera en ny användare"""
        self.username = f"user{random.randint(1, 100000)}"
        self.password = "TestPass123"

        # Försök att registrera en användare
        with self.client.post("/register", data={"username": self.username, "password": self.password}, catch_response=True) as response:
            if response.status_code == 200:
                print(f"User {self.username} registered.")
        
        # Logga in med användaren
        with self.client.post("/login", data={"username": self.username, "password": self.password}, catch_response=True) as response:
            if response.status_code == 200:
                print(f"User {self.username} logged in.")
            else:
                print(f"Login failed for {self.username}")

    @task(3)
    def load_homepage(self):
        """Besöker startsidan"""
        self.client.get("/")

    @task(2)
    def view_products(self):
        """Visar produktkatalogen"""
        self.client.get("/products")

    @task(3)
    def add_product_to_cart(self):
        """Lägger en slumpmässig produkt i kundvagnen"""
        product_id = random.randint(1, 50)  # Anta att vi har 50 produkter
        self.client.post("/cart/add", data={"product_id": product_id, "quantity": 1})

    @task(1)
    def checkout(self):
        """Försöker checka ut"""
        self.client.post("/cart/checkout")

    @task(1)
    def logout(self):
        """Loggar ut användaren"""
        self.client.get("/logout")
