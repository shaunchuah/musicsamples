from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from playwright.sync_api import expect, sync_playwright

User = get_user_model()


class TestE2E(StaticLiveServerTestCase):
    def setUp(self):
        # Create a test user
        self.email = "test@example.com"
        self.password = "testpassword123"
        self.user = User.objects.create_user(email="test@example.com", password=self.password)

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch()
        self.page = self.browser.new_page()

    def tearDown(self):
        self.browser.close()
        self.playwright.stop()

    def test_has_title(self):
        self.page.goto(self.live_server_url)

        # Expect a title "to contain" a substring.
        expect(self.page).to_have_title("G-Trac")

    def test_login(self):
        # Navigate to the login page
        self.page.goto(f"{self.live_server_url}/login/")

        # Fill in login form
        self.page.fill("input[name='email']", self.email)
        self.page.fill("input[name='password']", self.password)

        # Click the login button and wait for navigation
        self.page.click("button[type='submit']")
        self.page.wait_for_load_state("networkidle")

        # Verify successful login - check for an element that appears after login
        # This could be a welcome message, dashboard element, etc.
        expect(self.page.locator(".sidebar")).to_be_visible()
