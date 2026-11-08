from datetime import timedelta

from django.contrib.auth.models import User
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APITestCase

from .billing import apply_event
from .models import Category, Club, Invitation, Membership, Player, Plans, Skills


def make_club(name="Club A", status=Club.ACTIVE, user="coach", role=Membership.OWNER, **kw):
    club = Club.objects.create(name=name, status=status, **kw)
    u = User.objects.create_user(user, f"{user}@example.com", "pw-12345-x")
    Membership.objects.create(user=u, club=club, role=role)
    cat = Category.objects.create(club=club, name="Technical")
    skill = Skills.objects.create(club=club, skill_name="Passing", comment="", category=cat)
    player = Player.objects.create(
        club=club, name="Doe", first_name="John", address="a", post_code="1", city="Berlin",
        society="FC", date_of_birth="2000-01-01", email_address="j@example.com",
    )
    return club, u, skill, player


class Base(APITestCase):
    def login(self, username="coach", password="pw-12345-x"):
        r = self.client.post("/api/auth/login/", {"username": username, "password": password})
        self.assertEqual(r.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {r.data['token']}")


class ApiTests(Base):
    def setUp(self):
        self.club, self.user, self.skill, self.player = make_club()

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
        self.assertEqual(self.client.post(url, {"ratings": [{"skill": self.skill.id, "value": 4}]}, format="json").status_code, 200)
        self.client.post(url, {"ratings": [{"skill": self.skill.id, "value": 2}]}, format="json")
        detail = self.client.get(f"/api/players/{self.player.id}/").data
        self.assertEqual(len(detail["evaluations"]), 1)
        self.assertEqual(detail["evaluations"][0]["value"], 2)
        self.assertEqual(detail["evaluations"][0]["modified_by"], "coach")
        bad = self.client.post(url, {"ratings": [{"skill": self.skill.id, "value": 9}]}, format="json")
        self.assertEqual(bad.status_code, 400)

    def test_dashboard(self):
        self.login()
        self.assertEqual(self.client.get("/api/dashboard/").data["players"], 1)


class TenancyTests(Base):
    def test_clubs_cannot_see_or_touch_each_other(self):
        _, _, skill_a, player_a = make_club("A", user="a")
        _, _, skill_b, player_b = make_club("B", user="b")
        self.login("b")
        self.assertEqual([p["id"] for p in self.client.get("/api/players/").data["results"]], [player_b.id])
        self.assertEqual(self.client.get(f"/api/players/{player_a.id}/").status_code, 404)
        self.assertEqual(self.client.delete(f"/api/players/{player_a.id}/").status_code, 404)
        # Cannot rate another club's player or use another club's skill.
        url = f"/api/players/{player_b.id}/evaluate/"
        r = self.client.post(url, {"ratings": [{"skill": skill_a.id, "value": 3}]}, format="json")
        self.assertEqual(r.status_code, 400)
        self.assertEqual(self.client.post(f"/api/players/{player_a.id}/evaluate/", {"ratings": []}, format="json").status_code, 404)


class RegistrationTrialTests(Base):
    def payload(self, **kw):
        return {"username": "newcoach", "email": "new@example.com", "password": "S3cure-pass-77", "club_name": "FC New", **kw}

    def test_register_creates_club_on_trial_with_starter_skills(self):
        r = self.client.post("/api/auth/register/", self.payload())
        self.assertEqual(r.status_code, 201)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {r.data['token']}")
        me = self.client.get("/api/auth/me/").data["club"]
        self.assertEqual((me["status"], me["entitled"], me["role"]), ("trialing", True, "owner"))
        self.assertGreater(len(self.client.get("/api/skills/").data), 5)

    def test_trial_is_one_time_per_email(self):
        self.assertEqual(self.client.post("/api/auth/register/", self.payload()).status_code, 201)
        again = self.client.post("/api/auth/register/", self.payload(username="other", email="NEW@example.com"))
        self.assertEqual(again.status_code, 400)
        self.assertIn("email", again.data)

    def test_weak_password_rejected(self):
        self.assertEqual(self.client.post("/api/auth/register/", self.payload(password="12345678")).status_code, 400)

    def test_expired_trial_is_blocked_with_402(self):
        club, *_ = make_club(status=Club.TRIALING, trial_ends_at=timezone.now() - timedelta(days=1))
        self.login()
        self.assertEqual(self.client.get("/api/players/").status_code, 402)
        self.assertEqual(self.client.get("/api/auth/me/").data["club"]["entitled"], False)

    def test_canceled_keeps_access_until_period_end(self):
        make_club(status=Club.CANCELED, current_period_end=timezone.now() + timedelta(days=3))
        self.login()
        self.assertEqual(self.client.get("/api/players/").status_code, 200)

    def test_checkout_not_configured_returns_501(self):
        make_club()
        self.login()
        self.assertEqual(self.client.post("/api/billing/checkout/").status_code, 501)


class StripeEventTests(Base):
    def test_events_update_club_status(self):
        club = Club.objects.create(name="X", status=Club.TRIALING, trial_ends_at=timezone.now() - timedelta(days=1))
        apply_event({"type": "checkout.session.completed", "data": {"object": {
            "client_reference_id": str(club.id), "customer": "cus_1", "subscription": "sub_1"}}})
        club.refresh_from_db()
        self.assertEqual((club.status, club.stripe_customer_id), (Club.ACTIVE, "cus_1"))
        self.assertTrue(club.is_entitled)
        end = int((timezone.now() + timedelta(days=5)).timestamp())
        apply_event({"type": "customer.subscription.updated", "data": {"object": {
            "id": "sub_1", "customer": "cus_1", "status": "past_due", "current_period_end": end}}})
        club.refresh_from_db()
        self.assertEqual(club.status, Club.PAST_DUE)
        self.assertTrue(club.is_entitled)  # grace until paid period ends
        apply_event({"type": "customer.subscription.deleted", "data": {"object": {"id": "sub_1", "customer": "cus_1"}}})
        club.refresh_from_db()
        self.assertEqual(club.status, Club.CANCELED)


@override_settings(MAX_SEATS=2)
class TeamTests(Base):
    def setUp(self):
        self.club, self.owner, self.skill, self.player = make_club()
        self.login()

    def test_invite_accept_flow_and_seat_limit(self):
        r = self.client.post("/api/team/invites/", {"email": "second@example.com", "role": "coach"}, format="json")
        self.assertEqual(r.status_code, 201)
        token = r.data["token"]
        self.client.credentials()  # anonymous visitor opens the invite
        self.assertEqual(self.client.get(f"/api/auth/invite/?token={token}").data["club_name"], "Club A")
        acc = self.client.post("/api/auth/accept-invite/", {"token": token, "username": "second", "password": "S3cure-pass-77"})
        self.assertEqual(acc.status_code, 201)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {acc.data['token']}")
        self.assertEqual(self.client.get("/api/players/").data["count"], 1)  # sees the same club data
        # Reusing the link fails; seat limit (2) is now full for the owner.
        self.client.credentials()
        self.assertEqual(self.client.get(f"/api/auth/invite/?token={token}").status_code, 404)
        self.login()
        full = self.client.post("/api/team/invites/", {"email": "third@example.com"}, format="json")
        self.assertEqual(full.status_code, 400)

    def test_coaches_and_viewers_cannot_manage_team_or_write(self):
        viewer = User.objects.create_user("viewer", "v@example.com", "pw-12345-x")
        Membership.objects.create(user=viewer, club=self.club, role=Membership.VIEWER)
        self.login("viewer")
        self.assertEqual(self.client.get("/api/players/").status_code, 200)
        self.assertEqual(self.client.delete(f"/api/players/{self.player.id}/").status_code, 403)
        self.assertEqual(self.client.post("/api/team/invites/", {"email": "x@example.com"}, format="json").status_code, 403)

    def test_owner_can_remove_member_but_not_self(self):
        u = User.objects.create_user("c2", "c2@example.com", "pw-12345-x")
        m = Membership.objects.create(user=u, club=self.club, role=Membership.COACH)
        self.assertEqual(self.client.delete(f"/api/team/members/{m.id}/").status_code, 204)
        self.assertFalse(User.objects.filter(username="c2").exists())
        own = self.club.memberships.get(user=self.owner)
        self.assertEqual(self.client.delete(f"/api/team/members/{own.id}/").status_code, 400)

    def test_expired_invite_rejected(self):
        inv = Invitation.objects.create(club=self.club, email="late@example.com", token="tok", created_at=timezone.now() - timedelta(days=30))
        self.client.credentials()
        self.assertEqual(self.client.get(f"/api/auth/invite/?token={inv.token}").status_code, 404)


class ShareTests(Base):
    def setUp(self):
        self.club, *_ = make_club()
        self.plan = Plans.objects.create(club=self.club, image="images/x.png", created_by="coach", comment="c", title="Press")
        self.login()

    def test_share_and_revoke(self):
        token = self.client.post(f"/api/plans/{self.plan.id}/share/").data["share_token"]
        self.client.credentials()  # public, no login
        public = self.client.get(f"/api/shared/{token}/")
        self.assertEqual((public.status_code, public.data["title"], public.data["club_name"]), (200, "Press", "Club A"))
        self.login()
        self.assertEqual(self.client.delete(f"/api/plans/{self.plan.id}/share/").status_code, 204)
        self.client.credentials()
        self.assertEqual(self.client.get(f"/api/shared/{token}/").status_code, 404)


class I18nTests(APITestCase):
    def test_login_error_follows_accept_language(self):
        for lang, expected in [("de", "Benutzername oder Passwort ist falsch."), ("en", "Invalid username or password.")]:
            r = self.client.post("/api/auth/login/", {"username": "x", "password": "y"}, headers={"Accept-Language": lang})
            self.assertEqual(r.status_code, 400)
            self.assertEqual(r.data["detail"], expected)

    def test_registration_errors_are_localized(self):
        User.objects.create_user("taken", "taken@example.com", "pw-12345-x")
        r = self.client.post(
            "/api/auth/register/", {"username": "new", "email": "taken@example.com", "password": "S3cure-pass-77", "club_name": "X"},
            headers={"Accept-Language": "de"},
        )
        self.assertEqual(r.status_code, 400)
        self.assertEqual(str(r.data["email"][0]), "Ein Konto mit dieser E-Mail-Adresse existiert bereits.")


class TrialKeyTests(Base):
    def payload(self, email, username):
        return {"username": username, "email": email, "password": "S3cure-pass-77", "club_name": "X"}

    def test_aliases_share_one_trial(self):
        self.assertEqual(self.client.post("/api/auth/register/", self.payload("jo.hn@gmail.com", "a1")).status_code, 201)
        for alias in ("john+promo@gmail.com", "J.O.H.N@googlemail.com", "JOHN@gmail.com"):
            r = self.client.post("/api/auth/register/", self.payload(alias, "u" + alias[:3]))
            self.assertEqual(r.status_code, 400, alias)

    def test_trial_key_is_unique_in_the_database(self):
        from django.db import IntegrityError, transaction
        Club.objects.create(name="A", trial_key="x@example.com")
        with self.assertRaises(IntegrityError), transaction.atomic():
            Club.objects.create(name="B", trial_key="x@example.com")


class AccessTests(Base):
    def test_login_without_a_club_is_refused(self):
        User.objects.create_user("staff", "s@example.com", "pw-12345-x", is_staff=True)
        r = self.client.post("/api/auth/login/", {"username": "staff", "password": "pw-12345-x"})
        self.assertEqual(r.status_code, 403)

    def test_only_the_owner_sees_invite_tokens(self):
        club, owner, *_ = make_club()
        Invitation.objects.create(club=club, email="new@example.com", token="secret-token")
        coach = User.objects.create_user("c", "c@example.com", "pw-12345-x")
        Membership.objects.create(user=coach, club=club, role=Membership.COACH)
        self.login("coach")
        self.assertIn("token", self.client.get("/api/team/").data["invites"][0])
        self.login("c")
        invite = self.client.get("/api/team/").data["invites"][0]
        self.assertNotIn("token", invite)
        self.assertEqual(invite["email"], "new@example.com")


class TestEnvironmentIsolationTests(APITestCase):
    def test_tests_never_use_real_services(self):
        from django.conf import settings
        self.assertEqual(settings.SETTINGS_MODULE, "web_application.settings_test")
        self.assertIn(settings.DATABASES["default"]["ENGINE"], ("django.db.backends.sqlite3", "django.db.backends.postgresql"))
        if settings.DATABASES["default"]["ENGINE"].endswith("postgresql"):
            self.assertTrue(settings.DATABASES["default"]["NAME"].startswith("test"))
        self.assertEqual((settings.STRIPE_SECRET_KEY, settings.EMAIL_BACKEND), ("", "django.core.mail.backends.locmem.EmailBackend"))
        self.assertTrue(settings.MEDIA_IS_LOCAL)


class MediaStorageTests(APITestCase):
    def build(self, **env):
        from web_application.storage import build_media_storage
        return build_media_storage(env)

    def test_local_is_the_default(self):
        self.assertEqual(self.build()["BACKEND"], "django.core.files.storage.FileSystemStorage")

    def test_s3_gcs_and_azure(self):
        s3 = self.build(MEDIA_STORAGE="s3", AWS_STORAGE_BUCKET_NAME="b", AWS_S3_ENDPOINT_URL="https://r2.example", MEDIA_PUBLIC="0")
        self.assertEqual(s3["BACKEND"], "storages.backends.s3.S3Storage")
        self.assertEqual((s3["OPTIONS"]["bucket_name"], s3["OPTIONS"]["endpoint_url"], s3["OPTIONS"]["querystring_auth"]), ("b", "https://r2.example", True))
        gcs = self.build(MEDIA_STORAGE="gcs", GS_BUCKET_NAME="g")
        self.assertEqual((gcs["BACKEND"], gcs["OPTIONS"]["querystring_auth"]), ("storages.backends.gcloud.GoogleCloudStorage", False))
        az = self.build(MEDIA_STORAGE="azure", AZURE_ACCOUNT_NAME="acct", AZURE_CONTAINER="media")
        self.assertEqual(az["BACKEND"], "storages.backends.azure_storage.AzureStorage")
        self.assertNotIn("account_key", az["OPTIONS"])

    def test_missing_or_unknown_configuration_fails_loudly(self):
        from django.core.exceptions import ImproperlyConfigured
        for env in ({"MEDIA_STORAGE": "s3"}, {"MEDIA_STORAGE": "gcs"}, {"MEDIA_STORAGE": "azure", "AZURE_ACCOUNT_NAME": "a"}, {"MEDIA_STORAGE": "ftp"}):
            with self.assertRaises(ImproperlyConfigured, msg=str(env)):
                self.build(**env)

    def test_every_backend_class_is_importable(self):
        from django.utils.module_loading import import_string
        for path in ("storages.backends.s3.S3Storage", "storages.backends.gcloud.GoogleCloudStorage", "storages.backends.azure_storage.AzureStorage"):
            import_string(path)


class ContactTests(APITestCase):
    def payload(self, **kw):
        return {"name": "Sam Coach", "email": "sam@example.com", "club": "FC Test", "message": "We would like the full version.", "locale": "de", **kw}

    def test_message_is_stored_and_emailed_without_login(self):
        from django.core import mail
        from .models import ContactMessage
        r = self.client.post("/api/contact/", self.payload())
        self.assertEqual(r.status_code, 201)
        saved = ContactMessage.objects.get()
        self.assertEqual((saved.email, saved.club, saved.locale), ("sam@example.com", "FC Test", "de"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("full version", mail.outbox[0].body)

    def test_honeypot_stores_nothing(self):
        from .models import ContactMessage
        r = self.client.post("/api/contact/", self.payload(website="http://spam.example"))
        self.assertEqual(r.status_code, 201)
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_validation(self):
        self.assertEqual(self.client.post("/api/contact/", self.payload(email="not-an-email")).status_code, 400)
        self.assertEqual(self.client.post("/api/contact/", self.payload(message="")).status_code, 400)
        self.assertEqual(self.client.post("/api/contact/", self.payload(message="x" * 5000)).status_code, 400)


class SignupSwitchTests(APITestCase):
    def test_closed_signups_refuse_registration_with_a_translated_message(self):
        payload = {"username": "n", "email": "n@example.com", "password": "S3cure-pass-77", "club_name": "X"}
        with override_settings(SIGNUPS_OPEN=False):
            r = self.client.post("/api/auth/register/", payload, headers={"Accept-Language": "de"})
        self.assertEqual(r.status_code, 403)
        self.assertEqual(r.data["detail"], "Die Registrierung ist derzeit geschlossen. Bitte kontaktieren Sie uns.")
        self.assertFalse(User.objects.filter(username="n").exists())
