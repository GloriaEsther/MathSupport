from django.http import HttpResponse

def home(request):
    return HttpResponse("<h1>Bienvenido a MathSupport</h1>")
