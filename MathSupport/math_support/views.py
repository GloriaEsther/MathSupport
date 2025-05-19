#views.py solo maneja las vistas y peticiones HTTP.
from django.shortcuts import render,redirect
from django.contrib import messages
from .db import UsuarioModel#esto es de la collection de usuarios
from .db import ProblemaModel #esto es de la collection de los problemas matematicos
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import io
import os
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render
from sympy import sympify, Eq
import sympy as sp
#pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Ajusta si es necesario

#UsuarioModel.registrar_usuario("prueba@email.com", "123456")#prueba
#from pix2tex.cli import LatexOCR  # Asegúrate que Pix2Tex esté instalado
from pix2text import Pix2Text
from pylatexenc.latex2text import LatexNodes2Text
from PIL import Image
import os
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.conf import settings


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
            except Exception as e:
                latex_result = "Error al procesar imagen"
                texto_legible = str(e)

            resultados.append({
                'latex': latex_result,
                'texto': texto_legible
            })

            os.remove(image_path)

        return render(request, 'funciones/result.html', {
            'resultados': resultados
        })

    return render(request, 'funciones/upload.html')

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

@csrf_exempt  # Solo si estás haciendo pruebas sin token CSRF
def resolver_problema(request):
    if request.method == 'POST':
        if 'imagen' not in request.FILES:
            return JsonResponse({'error': 'No se envió ninguna imagen'}, status=400)

        imagen = request.FILES['imagen']
        img = Image.open(io.BytesIO(imagen.read()))
        
        ecuacion = pytesseract.image_to_string(img, config='--psm 6')
        ecuacion = ecuacion.strip()

        if not ecuacion:
            return JsonResponse({'error': 'No se pudo extraer texto de la imagen'}, status=400)

        problemas_existentes = ProblemaModel.buscar_problemas_por_ecuacion(ecuacion)

        if problemas_existentes:
            return JsonResponse({
                'mensaje': 'Problema encontrado en la base de datos',
                'problemas': problemas_existentes,
                'ecuacion': ecuacion
            })
        else:
            return JsonResponse({
                'mensaje': 'Problema no encontrado',
                'ecuacion': ecuacion
            })
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)
'''


#esto sabra dios si sirva xd :b
@csrf_exempt
def resolver_ecuacion(request):
 '''
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
     '''
 print("Luego resuelve")
 return render(request,"funciones/resolver.html")

'''
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