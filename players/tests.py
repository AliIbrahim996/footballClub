from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from .models import Category, Player, Skills


class ApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("coach", password="pw-12345-x")
        cat = Category.objects.create(name="Technical")
        self.skill = Skills.objects.create(skill_name="Passing", comment="", category=cat)
        self.player = Player.objects.create(
            name="Doe", first_name="John", address="a", post_code="1", city="Berlin",
            society="FC", date_of_birth="2000-01-01", email_address="j@example.com",
        )

    def login(self):
        r = self.client.post("/api/auth/login/", {"username": "coach", "password": "pw-12345-x"})
        self.assertEqual(r.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {r.data['token']}")

    def test_requires_auth(self):
        self.assertEqual(self.client.get("/api/players/").status_code, 401)

    def test_bad_login(self):
        r = self.client.post("/api/auth/login/", {"username": "coach", "password": "nope"})
        self.assertEqual(r.status_code, 400)

    def test_player_crud_and_validation(self):
        self.login()
        self.assertEqual(self.client.get("/api/players/").data["count"], 1)
        bad = self.client.post("/api/players/", {"name": "D0e", "first_name": "A"}, format="json")
        self.assertEqual(bad.status_code, 400)

    def test_evaluate_upserts_ratings(self):
        self.login()
        url = f"/api/players/{self.player.id}/evaluate/"
        r = self.client.post(url, {"ratings": [{"skill": self.skill.id, "value": 4}]}, format="json")
        self.assertEqual(r.status_code, 200)
        self.client.post(url, {"ratings": [{"skill": self.skill.id, "value": 2}]}, format="json")
        detail = self.client.get(f"/api/players/{self.player.id}/").data
        self.assertEqual(len(detail["evaluations"]), 1)
        self.assertEqual(detail["evaluations"][0]["value"], 2)
        self.assertEqual(detail["evaluations"][0]["modified_by"], "coach")
        out_of_range = self.client.post(url, {"ratings": [{"skill": self.skill.id, "value": 9}]}, format="json")
        self.assertEqual(out_of_range.status_code, 400)

    def test_dashboard(self):
        self.login()
        self.assertEqual(self.client.get("/api/dashboard/").data["players"], 1)


class I18nTests(APITestCase):
    def test_login_error_follows_accept_language(self):
        for lang, expected in [("de", "Benutzername oder Passwort ist falsch."), ("en", "Invalid username or password.")]:
            r = self.client.post("/api/auth/login/", {"username": "x", "password": "y"}, headers={"Accept-Language": lang})
            self.assertEqual(r.status_code, 400)
            self.assertEqual(r.data["detail"], expected)
