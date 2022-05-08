from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from userauth.models import Transactions


from django.urls import reverse


APICLIENT = APIClient()


class TestAccount(APITestCase):
    def setUp(self):
        User.objects.create_user(username="testuser", password="password")

    def test_user_login(self):
        data = {"username": "testuser", "password": "password"}
        login_url = reverse("login")
        log_in = APICLIENT.post(login_url, data, format="json")
        self.assertEqual(log_in.status_code, 200)
        self.assertIsInstance(log_in.json().get("access"), str)

    def test_add_new_transaction(self):

        User.objects.create_user(username="testuser2", password="password")
        data = {"username": "testuser", "password": "password"}
        login_url = reverse("login")
        log_in = APICLIENT.post(login_url, data, format="json")
        transaction_data = {
            "transaction_with": User.objects.get(username="testuser2").id,
            "transaction_type": "lend",
            "reason": "test",
            "amount": 100,
        }

        headers = {"HTTP_AUTHORIZATION": f'Bearer {log_in.json().get("access")}'}
        post_url = reverse("add_transaction")
        post_transation = self.client.post(post_url, transaction_data, **headers)
        self.assertEqual(post_transation.status_code, 201)

    def test_get_transactions(self):
        login_url = reverse("login")
        data = {"username": "testuser", "password": "password"}
        log_in = self.client.post(login_url, data, format="json")
        headers = {"HTTP_AUTHORIZATION": f'Bearer {log_in.json().get("access")}'}

        get_url = reverse("get_transactions")
        get_transations = self.client.get(get_url, **headers)
        self.assertEqual(get_transations.status_code, 200)

    def test_markpaid_transaction(self):
        User.objects.create_user(username="testuser2", password="password")

        login_url = reverse("login")
        data = {"username": "testuser", "password": "password"}
        log_in = self.client.post(login_url, data, format="json")
        headers = {"HTTP_AUTHORIZATION": f'Bearer {log_in.json().get("access")}'}
        transaction_data = {
            "transaction_with": User.objects.get(username="testuser2").id,
            "transaction_type": "lend",
            "reason": "test",
            "amount": 100,
        }
        post_url = reverse("add_transaction")
        post_transation = self.client.post(post_url, transaction_data, **headers)

        transaction_id = post_transation.json().get("result").get("id")

        get_url = reverse("mark_paid", args=[transaction_id])
        paid_transation = self.client.patch(get_url, **headers)
        self.assertEqual(paid_transation.status_code, 205)

        transaction2_data = {
            "transaction_with": User.objects.get(username="testuser2").id,
            "transaction_type": "borrow",
            "reason": "test",
            "amount": 100,
        }
        post_transation = self.client.post(post_url, transaction2_data, **headers)

        transaction2_data = {
            "transaction_with": User.objects.get(username="testuser2").id,
            "transaction_type": "",
            "reason": "test",
            "amount": 100,
        }
        post_transation = self.client.post(post_url, transaction2_data, **headers)

    def test_all_users(self):
        login_url = reverse("login")
        data = {"username": "testuser", "password": "password"}
        log_in = self.client.post(login_url, data, format="json")
        headers = {"HTTP_AUTHORIZATION": f'Bearer {log_in.json().get("access")}'}
        all_users_url = reverse("users")
        all_users = self.client.get(all_users_url, **headers)
        self.assertEqual(all_users.status_code, 200)
