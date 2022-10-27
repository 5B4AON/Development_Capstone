from urllib.error import HTTPError
from requests import Response
from unittest.mock import Mock, patch
from django.test import TestCase
from djangoapp.restapis import get_dealers, get_reviews, post_review


class BackendApiTest(TestCase):

    def setUp(self):
        pass

    @patch('requests.post')
    def test_get_dealers_success(self, mock_post):
        mock_post.return_value.status_code = 200
        json_val = {"response": {"result": {
            "rows": [{"doc": ""}, {"doc": ""}]}}}
        mock_post.return_value.json = Mock(return_value=json_val)
        self.assertEqual(len(get_dealers()), 2)
        json_val = {"response": {"result": {"docs": [{}, {}]}}}
        mock_post.return_value.json = Mock(return_value=json_val)
        self.assertEqual(len(get_dealers("state")), 2)

    @patch('requests.post')
    def test_get_dealers_not_200(self, mock_post):
        mock_post.return_value.status_code = 403
        mock_post.return_value.reason = "Forbidden"
        self.assertRaisesMessage(HTTPError, "Forbidden", get_dealers)
        self.assertRaisesMessage(HTTPError, "Forbidden", get_dealers, "state")

    @patch('requests.post')
    def test_get_dealers_500(self, mock_post):
        mock_post.return_value = None  # Causes an AttributeError to be raised
        self.assertRaisesMessage(
            HTTPError, "Something went wrong on the server.", get_dealers)
        self.assertRaisesMessage(
            HTTPError, "Something went wrong on the server.", get_dealers, "state")

    @patch('requests.post')
    def test_get_dealers_empty(self, mock_post):
        mock_post.return_value.status_code = 200
        json_val = {"response": {"result": {"rows": []}}}
        mock_post.return_value.json = Mock(return_value=json_val)
        self.assertRaisesMessage(
            HTTPError, "The database is empty.", get_dealers)
        json_val = {"response": {"result": {"docs": []}}}
        mock_post.return_value.json = Mock(return_value=json_val)
        self.assertRaisesMessage(
            HTTPError, "The state does not exist.", get_dealers, "state")

    @patch('requests.post')
    def test_get_reviews_success(self, mock_post):
        mock_post.return_value.status_code = 200
        json_val = {"response": {"result": {"docs": [{}, {}]}}}
        mock_post.return_value.json = Mock(return_value=json_val)
        self.assertEqual(len(get_reviews(0)), 2)

    @patch('requests.post')
    def test_get_reviews_not_200(self, mock_post):
        mock_post.return_value.status_code = 403
        mock_post.return_value.reason = "Forbidden"
        self.assertRaisesMessage(HTTPError, "Forbidden", get_reviews, 0)

    @patch('requests.post')
    def test_get_reviews_500(self, mock_post):
        mock_post.return_value = None  # Causes an AttributeError to be raised
        self.assertRaisesMessage(
            HTTPError, "Something went wrong on the server.", get_reviews, 0)

    @patch('requests.post')
    def test_get_reviews_empty(self, mock_post):
        mock_post.return_value.status_code = 200
        json_val = {"response": {"result": {"docs": []}}}
        mock_post.return_value.json = Mock(return_value=json_val)
        self.assertRaisesMessage(
            HTTPError, "The dealer Id does not exist.", get_reviews, 0)

    @patch('requests.post')
    def test_post_review_success(self, mock_post):
        mock_post.return_value.status_code = 200
        json_val = {"response": {"result": {
            "id": "123", "ok": True, "rev": "1"}}}
        mock_post.return_value.json = Mock(return_value=json_val)
        self.assertEqual(post_review({}), True)

    @patch('requests.post')
    def test_post_review_not_200(self, mock_post):
        mock_post.return_value.status_code = 403
        mock_post.return_value.reason = "Forbidden"
        self.assertRaisesMessage(HTTPError, "Forbidden", post_review, {})

    @patch('requests.post')
    def test_post_review_500(self, mock_post):
        mock_post.return_value = None  # Causes an AttributeError to be raised
        self.assertRaisesMessage(
            HTTPError, "Something went wrong on the server.", post_review, {})

    @patch('requests.post')
    def test_post_review_failure(self, mock_post):
        mock_post.return_value.status_code = 200
        json_val = {"response": {"result": {"ok": False}}}
        mock_post.return_value.json = Mock(return_value=json_val)
        self.assertEqual(post_review({}), False)

        # mock_post.return_value = Mock( # simulate the response object
        #     spec=Response,             # based on the actual Response object as a template
        #     status_code=200,           # overwrite response.status_code
        #     json=Mock(return_value=...) # overwrite response.json()
        # )
