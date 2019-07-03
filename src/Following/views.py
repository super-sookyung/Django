from django.shortcuts import render
from django.http import HttpResponse
def index(request):
	return HttpResponse("Hello, you have entered 'Follow'.")
# def show_follower(request):
	