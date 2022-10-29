from urllib.error import HTTPError
from unittest.mock import Mock, patch
from django.test import TestCase
from djangoapp.restapis import get_dealers, get_reviews, post_review, analyze_review_sentiments
from ibm_watson import ApiException, NaturalLanguageUnderstandingV1


class BackendApiTest(TestCase):

    def setUp(self):
        self.sample_dealership = {
            "_id": "4dbd6312b1c7fffb175437775c06d05b",
            "_rev": "1-7828b3ead20b34e43a00d8305fee6cd2",
            "address": "2109 Scott Parkway",
            "city": "San Francisco",
            "full_name": "It Car Dealership",
            "id": 14,
            "lat": 37.7848,
            "long": -122.7278,
            "short_name": "It",
            "st": "CA",
            "state": "California",
            "zip": "94147"
        }
        self.sample_review = {
            "car_make": "Audi",
            "car_model": "Car",
            "car_year": 2021,
            "dealership": 15,
            "id": 0,
            "name": "Upkar Lidder",
            "purchase": False,
            "purchase_date": "02/16/2021",
            "review": "Great service!"
        }

    @patch('requests.post')
    def test_get_dealers_success(self, mock_post):
        mock_post.return_value.status_code = 200

        json_val = {"response": {"result": {
            "rows": [{"doc": self.sample_dealership}, {"doc": self.sample_dealership}]}}}
        mock_post.return_value.json = Mock(return_value=json_val)
        self.assertEqual(len(get_dealers()), 2)
        self.assertEqual(get_dealers()[0].full_name, "It Car Dealership")

        json_val = {"response": {"result": {"docs": [self.sample_dealership, self.sample_dealership]}}}
        mock_post.return_value.json = Mock(return_value=json_val)
        self.assertEqual(len(get_dealers(st="CA")), 2)
        self.assertEqual(get_dealers(st="CA")[0].full_name, "It Car Dealership")

    @patch('requests.post')
    def test_get_dealers_not_200(self, mock_post):
        mock_post.return_value.status_code = 403
        mock_post.return_value.reason = "Forbidden"
        self.assertRaisesMessage(HTTPError, "Forbidden", get_dealers)
        self.assertRaisesMessage(HTTPError, "Forbidden", get_dealers, st="CA")

    @patch('requests.post')
    def test_get_dealers_500(self, mock_post):
        mock_post.return_value = None  # Causes an AttributeError to be raised
        self.assertRaisesMessage(
            HTTPError, "Something went wrong on the server.", get_dealers)
        self.assertRaisesMessage(
            HTTPError, "Something went wrong on the server.", get_dealers, st="CA")

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
            HTTPError, "Dealership not found.", get_dealers, st="CA")

    @patch('requests.post')
    @patch('djangoapp.restapis.analyze_review_sentiments')
    def test_get_reviews_success(self, mock_analyze, mock_post):
        mock_post.return_value.status_code = 200
        json_val = {"response": {"result": {"docs": [self.sample_review]}}}
        mock_post.return_value.json = Mock(return_value=json_val)
        mock_analyze.return_value = "positive"
        self.assertEqual(len(get_reviews(id=0)), 1)

    @patch('requests.post')
    @patch('djangoapp.restapis.analyze_review_sentiments')
    def test_get_reviews_nlu_exception(self, mock_analyze, mock_post):
        mock_post.return_value.status_code = 200
        json_val = {"response": {"result": {"docs": [self.sample_review]}}}
        mock_post.return_value.json = Mock(return_value=json_val)
        mock_analyze.side_effect = ApiException(code=400, message="Bad request")
        self.assertRaisesMessage(HTTPError, "Bad request", get_reviews, id=0)

    @patch.object(NaturalLanguageUnderstandingV1, 'analyze')
    def test_analyze_review_sentiments(self, mock_analyze):
        mock_analyze.return_value.get_result = Mock(return_value={"sentiment": {"document": {"label": "testing"}}})
        self.assertEqual(analyze_review_sentiments("test"), "testing")

    @patch('requests.post')
    def test_get_reviews_not_200(self, mock_post):
        mock_post.return_value.status_code = 403
        mock_post.return_value.reason = "Forbidden"
        self.assertRaisesMessage(HTTPError, "Forbidden", get_reviews, id=0)

    @patch('requests.post')
    def test_get_reviews_500(self, mock_post):
        mock_post.return_value = None  # Causes an AttributeError to be raised
        self.assertRaisesMessage(
            HTTPError, "Something went wrong on the server.", get_reviews, id=0)

    @patch('requests.post')
    def test_get_reviews_empty(self, mock_post):
        mock_post.return_value.status_code = 200
        json_val = {"response": {"result": {"docs": []}}}
        mock_post.return_value.json = Mock(return_value=json_val)
        self.assertRaisesMessage(
            HTTPError, "No reviews yet...", get_reviews, id=0)

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

