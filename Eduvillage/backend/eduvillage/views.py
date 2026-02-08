from django.http import HttpResponse

def home(request):
    return HttpResponse("Eduvillage backend is running successfully 🚀")
