import requests
import json
import os
from ibm_watson import NaturalLanguageUnderstandingV1, ApiException
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions
from .models import CarDealer, DealerReview
from urllib.error import HTTPError
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

cf_user = os.environ['cfUser']
cf_pass = os.environ['cfPass']
cloudant_dealership_url = os.environ['dealershipUrl']
cloudant_review_url = os.environ['reviewUrl']
cloudant_review_post_url = os.environ['reviewPostUrl']
nlu_key = os.environ['nluKey']
nlu_url = os.environ['nluUrl']


def post_request_to_cf(url, payload):
    ''' IAM authenticated post request to IBM Cloud functions '''
    # When using IAM authentication GET requests do not work
    # Exceptions are handled down the line by the calling functions
    response = requests.post(
        url,
        data=json.dumps(payload),
        headers={'Content-Type': 'application/json'},
        auth=HTTPBasicAuth(cf_user, cf_pass)
    )
    return response


def get_dealers(**kwargs):
    ''' Get all dealerships without args or based on st=? or id=?'''
    result = []
    try:
        response = post_request_to_cf(cloudant_dealership_url, kwargs)
        if response.status_code == 200:
            if len(kwargs) == 0:
                jsonResponse = response.json()["response"]["result"]["rows"]
                for item in jsonResponse:
                    doc = item["doc"]
                    dealer = CarDealer(address=doc["address"], city=doc["city"],
                                       full_name=doc["full_name"], id=doc["id"],
                                       lat=doc["lat"], long=doc["long"],
                                       short_name=doc["short_name"], st=doc["st"],
                                       state=doc["state"], zip=doc["zip"])
                    result.append(dealer)
            else:
                jsonResponse = response.json()["response"]["result"]["docs"]
                for item in jsonResponse:
                    dealer = CarDealer(address=item["address"], city=item["city"],
                                       full_name=item["full_name"], id=item["id"],
                                       lat=item["lat"], long=item["long"],
                                       short_name=item["short_name"], st=item["st"],
                                       state=item["state"], zip=item["zip"])
                    result.append(dealer)
        else:
            raise HTTPError(cloudant_dealership_url, response.status_code,
                            response.reason, None, None)
    except HTTPError:
        # If we already have an HTTPError then do not recast just throw
        raise
    except:
        raise HTTPError(cloudant_dealership_url, 500,
                        "Something went wrong on the server.", None, None)
    if len(result) == 0:
        if len(kwargs) == 0:
            raise HTTPError(cloudant_dealership_url, 404,
                            "The database is empty.", None, None)
        raise HTTPError(cloudant_dealership_url, 404,
                        "Dealership not found.", None, None)
    return result


def get_reviews(**kwargs):
    ''' Get reviews based on dealership id=?'''
    result = []
    try:
        response = post_request_to_cf(cloudant_review_url, kwargs)
        if response.status_code == 200:
            jsonResponse = response.json()["response"]["result"]["docs"]
            for item in jsonResponse:
                sentiment = analyze_review_sentiments(item["review"])
                review = DealerReview(car_make=item["car_make"], car_model=item["car_model"],
                                   car_year=item["car_year"], dealership=item["dealership"],
                                   id=item["id"], name=item["name"],
                                   purchase=item["purchase"], purchase_date=item["purchase_date"],
                                   review=item["review"], sentiment=sentiment)
                result.append(review)
        else:
            raise HTTPError(cloudant_review_url, response.status_code,
                            response.reason, None, None)
    except HTTPError:
        # If we already have an HTTPError then do not recast just throw
        raise
    except ApiException as ex:
        # handle NLU api exceptions
        raise HTTPError(cloudant_review_url, ex.code,
                        ex.message, None, None)        
    except Exception as ex:
        raise HTTPError(cloudant_review_url, 500,
                        "Something went wrong on the server.", None, None)
    if len(result) == 0:
        raise HTTPError(cloudant_review_url, 404,
                        "Reviews not found.", None, None)
    return result


def post_review(review):
    ''' Post a new review given a json review object '''
    payload = {
        "review": review
    }
    result = False
    try:
        response = post_request_to_cf(cloudant_review_post_url, payload)
        if response.status_code == 200:
            result = response.json()["response"]["result"]["ok"]
        else:
            raise HTTPError(cloudant_review_url, response.status_code,
                            response.reason, None, None)
    except HTTPError:
        # If we already have an HTTPError then do not recast just throw
        raise
    except:
        raise HTTPError(cloudant_review_url, 500,
                        "Something went wrong on the server.", None, None)
    return result


def analyze_review_sentiments(text):
    auth = IAMAuthenticator(nlu_key)
    client = NaturalLanguageUnderstandingV1(
        version='2022-04-07',
        authenticator=auth
    )
    client.set_service_url(nlu_url)
    features = Features(sentiment=SentimentOptions())
    response = client.analyze(text=text, language='en', features=features).get_result()
    return response["sentiment"]["document"]["label"]





    

