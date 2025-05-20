#views.py solo maneja las vistas y peticiones HTTP.
from django.shortcuts import render,redirect
from django.contrib import messages
from .db import UsuarioModel#esto es de la collection de usuarios
from .db import ProblemaModel #esto es de la collection de los problemas matematicos
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import io
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render
from sympy import sympify, Eq
import sympy as sp
from pix2text import Pix2Text
from pylatexenc.latex2text import LatexNodes2Text
from PIL import Image
import os
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.conf import settings

#OCR
# Carga el modelo una sola vez
model = Pix2Text(model_name='mfr')#para ejercicios manuscritos
#la vista de abajo tambien funciona pero aun hay que mejorar
'''
18-05-25

@csrf_exempt
def ocr_view(request):
    resultados = []

    if request.method == 'POST' and request.FILES.getlist('images'):
        images = request.FILES.getlist('images')
        fs = FileSystemStorage()

        for image_file in images:
            filename = fs.save(image_file.name, image_file)
            image_path = fs.path(filename)

            try:
                image = Image.open(image_path).convert('RGB')
                latex_result = model.recognize(image)  # Usa Pix2Text
                texto = LatexNodes2Text().latex_to_text(latex_result)
                resultados.append(texto)
            except Exception as e:
                resultados.append(f"Error al procesar imagen: {str(e)}")

            os.remove(image_path)

    return render(request, 'funciones/upload.html', {
        'resultados': resultados
    })
'''

#19/05/2025
#esto funciona pero la no negatividad la pone despues de la funcion objetivo 
@csrf_exempt
def ocr_view(request):
    if request.method == 'POST' and request.FILES.getlist('images'):
        files = request.FILES.getlist('images')
        resultados = []

        for image_file in files:
            fs = FileSystemStorage()
            filename = fs.save(image_file.name, image_file)
            image_path = fs.path(filename)

            try:
                image = Image.open(image_path).convert('RGB')
                latex_result = model.recognize(image)
                texto_legible = LatexNodes2Text().latex_to_text(latex_result)
                #texto_ordenado = limpiar_y_ordenar(texto_legible)
            except Exception as e:
                latex_result = "Error al procesar imagen"
                texto_legible = str(e) #eso estaba primero
                #texto_ordenado=str(e)

            resultados.append({
                'latex': latex_result,
                'texto': texto_legible #eso estaba primero
                #'texto':texto_ordenado
            })

            os.remove(image_path)

        return render(request, 'funciones/result.html', {
            'resultados': resultados
        })

    return render(request, 'funciones/upload.html')

@csrf_exempt
def resolver_ecuacion(request):
 print("Luego resuelve")
 return render(request,"funciones/resolver.html")

#login
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