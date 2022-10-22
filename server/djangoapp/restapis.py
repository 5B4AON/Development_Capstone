from operator import add
import requests
import json
import os
# import related models here
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError
from dotenv import load_dotenv

load_dotenv()

api_user = os.environ['apiUser']
api_pass = os.environ['apiPass']
couch_db_key = os.environ['couchDbKey']
couch_db_url = os.environ['couchDbUrl']
dealership_url = os.environ['dealershipUrl']
review_url = os.environ['reviewUrl']
review_post_url = os.environ['reviewPostUrl']


def post_request(url, payload):
    try:
        response = requests.post(url, data=json.dumps(payload), headers={'Content-Type': 'application/json'}, auth=HTTPBasicAuth(api_user, api_pass))
        response.raise_for_status()
        return response
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')


def get_dealers_from_cf():
    payload = {
        "IAM_API_KEY": couch_db_key,
        "COUCH_URL": couch_db_url
    }
    response = post_request(dealership_url, payload)
    jsonResponse = response.json()["response"]["result"]["rows"]
    result = []
    for item in jsonResponse:
        result.append(item["doc"])
    return result


def get_state_dealers_from_cf(state):
    payload = {
        "IAM_API_KEY": couch_db_key,
        "COUCH_URL": couch_db_url,
        "STATE": state
    }
    response = post_request(dealership_url, payload)
    jsonResponse = response.json()
    result = jsonResponse["response"]["result"]["docs"]
    return result


def get_dealer_reviews_by_id_from_cf(dealerId):
    payload = {
        "IAM_API_KEY": couch_db_key,
        "COUCH_URL": couch_db_url,
        "DEALER_ID": dealerId
    }
    response = post_request(review_url, payload)
    jsonResponse = response.json()
    result = jsonResponse["response"]["result"]["docs"]
    return result


def post_dealer_review_to_cf(review):
    payload = {
        "IAM_API_KEY": couch_db_key,
        "COUCH_URL": couch_db_url,
        "REVIEW": review
    }
    post_request(review_post_url, payload)


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative



