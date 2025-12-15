from django.http import HttpResponse

def homepage(request):
    return HttpResponse("Hello world! i am shahin")

def about(request):
    return HttpResponse("about page.")