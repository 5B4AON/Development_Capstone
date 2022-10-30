from urllib.error import HTTPError
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from .models import CarModel, CarMake
from .restapis import get_dealers, get_reviews, post_review
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


def about(request):
    """ Render a static About Us page """
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)


def contact(request):
    """ Render a static Contact Us page """
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html', context)


def login_request(request):
    """ Handle a Login request """
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
    return redirect('djangoapp:index')


def logout_request(request):
    """ Handle Logout request """
    logout(request)
    return redirect('djangoapp:index')


def registration_request(request):
    """ Handle Sign Up request """
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exists = False
        try:
            # Check if user already exists
            User.objects.get(username=username)
            user_exists = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))
        # If it is a new user
        if not user_exists:
            # Create user in auth_user table
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            # Login the user and redirect to course list page
            login(request, user)
            return redirect("djangoapp:index")
        else:
            # Return message that user already exists
            context["message"] = "User already exists"
            return render(request, 'djangoapp/registration.html', context)


def get_dealerships(request):
    """ Render page with a list of dealerships """
    context = {}
    if request.method == "GET":
        try:
            context["dealerships"] = get_dealers()
            return render(request, 'djangoapp/index.html', context)
        except HTTPError as e:
            context["message"] = e.reason
            return render(request, 'djangoapp/index.html', context)


def get_dealerships_proxy(request):
    """ Proxy for Cloud Function public GET request api/dealership """
    if request.method == "GET":
        try:
            dealerships = get_dealers()
            result = '<br />'.join([str(dealer).replace(" ", "&nbsp").replace(
                "\n", "<br />\n") for dealer in dealerships])
        except HTTPError as e:
            result = str(e.reason)
        return HttpResponse(result)


def get_state_dealerships_proxy(request, state):
    """ Proxy for Cloud Function public GET request api/dealership/<str:state> """
    if request.method == "GET":
        try:
            dealerships = get_dealers(st=state)
            result = '<br />'.join([str(dealer).replace(" ", "&nbsp").replace(
                "\n", "<br />\n") for dealer in dealerships])
        except HTTPError as e:
            result = str(e.reason)
        return HttpResponse(result)


def get_dealer_details(request, dealerId):
    """ Render page with dealer reviews """
    context = {}
    if request.method == "GET":
        try:
            context["dealer"] = get_dealers(id=dealerId)[0]
            context["reviews"] = get_reviews(id=dealerId)
            return render(request, 'djangoapp/dealer_details.html', context)
        except HTTPError as e:
            context["message"] = e.reason
            return render(request, 'djangoapp/dealer_details.html', context)


def get_dealer_details_proxy(request, dealerId):
    """ Proxy for Cloud Function public GET request api/review/<int:dealerId> """
    if request.method == "GET":
        try:
            reviews = get_reviews(id=dealerId)
            result = '<br />'.join([str(review).replace(" ", "&nbsp").replace("\n", "<br />\n") for review in reviews])
        except HTTPError as e:
            result = str(e.reason)
        return HttpResponse(result)


def add_review(request, dealerId):
    """ Post a review and then redirect to review page"""
    if not request.user.is_authenticated:
        return HttpResponse(status=401)
    context = {}
    try:
        if request.method == "GET":
            context["cars"] = CarModel.objects.filter(
                dealer_id=dealerId).select_related("make")
            context["dealer"] = get_dealers(id=dealerId)[0]
            return render(request, 'djangoapp/add_review.html', context)

        if request.method == "POST":
            car = CarModel.objects.get(id=request.POST.get("car"))
            print(car.make.name, car.name, car.year)
            review = {
                "car_make": car.make.name,
                "car_model": car.name,
                "car_year": car.year.strftime("%Y"),
                "dealership": dealerId,
                "id": 0,  # irrelevant as Cloudant autogenerates its own _id
                "name": request.POST.get("name"),
                "purchase": request.POST.get("purchasecheck") == 'on',
                "purchase_date": request.POST.get("purchasedate"),
                "review": request.POST.get("content")
            }
            post_review(review)
            return redirect("djangoapp:details", dealerId)
    except HTTPError as e:
        context["message"] = e.reason
        return render(request, 'djangoapp/add_review.html', context)
