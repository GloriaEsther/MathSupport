from django.shortcuts import render,redirect
from django.contrib import messages
#from .models import UsuarioModel
from .db import UsuarioModel#esto es de la base de datos
from django.views.decorators.csrf import csrf_exempt
###########################################
#views.py solo maneja las vistas y peticiones HTTP.
import pytesseract
from PIL import Image
import sympy as sp

# Configurar la ruta de Tesseract en Windows (si es necesario)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
#UsuarioModel.registrar_usuario("prueba@email.com", "123456")#prueba
@csrf_exempt#esta etiqueta es una "proteccion" contra falsificaciones de solicitudes entre sitios (CSRF)
def bienvenida(request):
    return render (request,"usuario/bienvenida.html")#ruta relativa


@csrf_exempt
def inicio_sesion(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        # Buscar usuario en la base de datos
        usuario = UsuarioModel.autenticar_usuario(email, password)
        if usuario:
            request.session['usuario_id'] = str(usuario['_id'])  # Guardar en sesión
            request.session['usuario_email'] = usuario['email'] 
            messages.success(request, "Inicio de sesión exitoso.")
            return redirect('home')  # Redirigir a la página principal(aun no existe xd)
        else:
            messages.error(request, "Correo o contraseña incorrectos.")
            return redirect('login')
    return render(request, 'usuario/login.html')#ruta relativa

@csrf_exempt
def registro(request):#ya funciona,falta el login :')
    if request.method == 'POST':
        print(f"📩 Datos recibidos en POST: {request.POST}")  # esto es para debug
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        print("Solicitud de registro recibida: email={email}, password={password}")

        if not email or not password:  # Si no se obtiene el email, mostrar un mensaje de error
            print("❌ Error: Campos vacíos")
            messages.error(request, "El campo email es obligatorio.")
            return redirect('registro')
        
        resultado = UsuarioModel.registrar_usuario(email, password)
        print("usuario: ",resultado)

        if "error" in resultado:
            messages.error(request, resultado["error"])
        else:
            messages.success(request, resultado["mensaje"])   

        messages.success(request, "Registro exitoso. Ahora puedes iniciar sesión.")

        return redirect('home')# return redirect('login')

    return render(request, "usuario/registro.html")
@csrf_exempt
def home(request):
    return render (request,"funciones/home.html")#ruta relativa
#esto no lo he probado aun
'''
def extraer_texto_de_imagen(ruta_imagen):
    imagen = Image.open(ruta_imagen)
    texto = pytesseract.image_to_string(imagen, lang='spa')  # o 'eng' si está en inglés
    return texto

'''





'''
esto sabra dios si sirva xd :b
@csrf_exempt
def resolver_ecuacion(request):
    
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            ecuacion = data.get("ecuacion")

            if not ecuacion:
                return JsonResponse({"error": "No se proporcionó una ecuación"}, status=400)

            x = sp.Symbol('x')
            solucion = sp.solve(ecuacion, x)
            return JsonResponse({"solucion": str(solucion)})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"mensaje": "Aquí se resolverán las ecuaciones"})
    
@csrf_exempt
def reconocer_ecuacion(request):
    
     if request.method == "POST" and request.FILES.get("imagen"):
        imagen = request.FILES["imagen"]
        img = Image.open(imagen)

        # Extraer texto de la imagen
        texto_reconocido = pytesseract.image_to_string(img)
        return JsonResponse({"ecuacion": texto_reconocido.strip()})

     return JsonResponse({"error": "No se proporcionó una imagen"}, status=400)

    #return JsonResponse({"mensaje": "Aquí se reconocerán ecuaciones con OCR"})
'''