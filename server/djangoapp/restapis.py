import requests
import json
import os
# import related models here
from urllib.error import HTTPError
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

api_user = os.environ['apiUser']
api_pass = os.environ['apiPass']
dealership_url = os.environ['dealershipUrl']
review_url = os.environ['reviewUrl']
review_post_url = os.environ['reviewPostUrl']


def post_request(url, payload):
    response = requests.post(
        url,
        data=json.dumps(payload),
        headers={'Content-Type': 'application/json'},
        auth=HTTPBasicAuth(api_user, api_pass)
    )
    return response


def get_dealers(state=None):
    payload = {}
    if state:
        payload["st"] = state
    result = []
    try:
        response = post_request(dealership_url, payload)
        if response.status_code == 200:
            if state:
                jsonResponse = response.json()["response"]["result"]["docs"]
                for item in jsonResponse:
                    result.append(item)
            else:
                jsonResponse = response.json()["response"]["result"]["rows"]
                for item in jsonResponse:
                    result.append(item["doc"])
        else:
            raise HTTPError(dealership_url, response.status_code,
                            response.reason, None, None)
    except HTTPError:
        raise
    except:
        raise HTTPError(dealership_url, 500,
                        "Something went wrong on the server.", None, None)
    if len(result) == 0:
        if state:
            raise HTTPError(dealership_url, 404,
                            "The state does not exist.", None, None)
        else:
            raise HTTPError(dealership_url, 404,
                            "The database is empty.", None, None)
    return result


def get_reviews(dealerId):
    payload = {
        "id": dealerId
    }
    result = []
    try:
        response = post_request(review_url, payload)
        if response.status_code == 200:
            jsonResponse = response.json()["response"]["result"]["docs"]
            for item in jsonResponse:
                result.append(item)
        else:
            raise HTTPError(review_url, response.status_code,
                            response.reason, None, None)
    except HTTPError:
        raise
    except:
        raise HTTPError(review_url, 500,
                        "Something went wrong on the server.", None, None)
    if len(result) == 0:
        raise HTTPError(review_url, 404,
                        "The dealer Id does not exist.", None, None)
    return result


def post_review(review):
    payload = {
        "review": review
    }
    result = {}
    try:
        response = post_request(review_post_url, payload)
        if response.status_code == 200:
            result = response.json()["response"]["result"]["ok"]
        else:
            raise HTTPError(review_url, response.status_code,
                            response.reason, None, None)
    except HTTPError:
        raise
    except:
        raise HTTPError(review_url, 500,
                        "Something went wrong on the server.", None, None)
    return result


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
