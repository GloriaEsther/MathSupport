#views.py solo maneja las vistas 
from django.shortcuts import render,redirect
from django.contrib import messages
from .db import UsuarioModel#esto es de la collection de usuarios
from .db import ProblemaModel #esto es de la collection de los problemas matematicos
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, FileResponse
#ocr librerias
from pix2text import Pix2Text
from pylatexenc.latex2text import LatexNodes2Text
from PIL import Image
import os
from django.core.files.storage import FileSystemStorage
from django.conf import settings
#resolucion de problemas librerias
import matplotlib.pyplot as plt
import re
from itertools import combinations
import io
from sympy import sympify, Eq
import numpy as np
import sympy as sp
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
import pickle  # Para serializar datos complejos como objetos sympy
import base64

'''
def reemplazar_variables_para_procesar(restricciones):#si ya reemplazo en el parseo segun yo ya no es necesario,igual lo dejo por las dudas
    reemplazos = {
        sp.Symbol('x1'): sp.Symbol('x'),
        sp.Symbol('x2'): sp.Symbol('y')
    }
    nuevas = []
    for r in restricciones:
        nuevo = r
        for viejo, nuevo_valor in reemplazos.items():
            nuevo = nuevo.replace(viejo, nuevo_valor)
        nuevas.append(nuevo)
    return nuevas
    
def reemplazar_variables_para_mostrar(pasos):
    reemplazos = {
       sp.Symbol('x1'): sp.Symbol('x'),
       sp.Symbol('x2'): sp.Symbol('y')
    }
    nuevos_pasos = []
    for paso in pasos:
        nuevo = paso
        for viejo, nuevo_valor in reemplazos.items():
            nuevo = nuevo.replace(viejo, nuevo_valor)
        nuevos_pasos.append(nuevo)
    return nuevos_pasos
'''



#OCR
# Carga el modelo una sola vez
model = Pix2Text(model_name='mfr')#para ejercicios manuscritos
#19/05/2025
#esto funciona pero la no negatividad la pone despues de la funcion objetivo
# vamos aver si con esto funciona:(hasta ahorita no c)
def mover_no_negatividad_al_final(restricciones):
    no_negativas = []
    otras = []
    fun_obj = []

    for r in restricciones:
         # Si r es un string, úsalo directamente
        if isinstance(r, dict):
            texto = r.get("contenido", "").strip().lower().replace(' ', '')
        elif isinstance(r, str):
            texto = r.strip().lower().replace(' ', '')
        else:
            continue  # ignora si no es string ni dict
        if "≥0" in texto or ">=0" in texto or "\\ge0" in texto or "ge0" in texto:
            no_negativas.append(r)#no negatividad 
        elif "Z" in texto or "z" in texto:
            fun_obj.append(r)#funcion objetivo
        else:
            otras.append(r)
    return fun_obj + otras + no_negativas

'''
#sospecho que es esto
def reemplazar_variables_en_pasos(pasos):
    reemplazos = {'x': 'x1', 'y': 'x2'}
    nuevos_pasos = []
    for paso in pasos:
        nuevo_paso = paso
        for viejo, nuevo_valor in reemplazos.items():
            nuevo_paso = nuevo_paso.replace(viejo, nuevo_valor)
        nuevos_pasos.append(nuevo_paso)
    return nuevos_pasos
'''
@csrf_exempt
def ocr_view(request):
    if request.method == 'POST' and request.FILES.getlist('images'):#recupera la lista de las imagenes ingresadas en el formulario
        files = request.FILES.getlist('images')#y las pasa a una lista
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
                texto_legible = str(e) #eso estaba primero
            
            resultados.append({#esta
                'latex': latex_result,
                'texto': texto_legible#, #eso estaba primero
            })

            os.remove(image_path)

            # Mover no negatividad al final
            Resultados= mover_no_negatividad_al_final(resultados)
     
        return render(request, 'funciones/result.html', {#result es en donde se muestra la ecuacion :b
            'resultados': Resultados#en las plantillas siempre se pone laa variables en minuscula al llamarlas a las plantillas(se llama a resultados)
        })

    return render(request, 'funciones/upload.html')

#resolucion de problemas (estamos en pruebas,ya muestra la grafica)
#22-05-2025
#declara variables
x, y = sp.symbols("x y")
x1, x2 = sp.symbols('x1 x2')  # estos se usan en la entrada del usuario#

variables = (x, y)

def limpiar_expresion(expr):#revisa que la expresion ingresada(lista) contenga una letra (como en la funcion objetivo usa Z como funcion (para maximizar))
    expr = expr.replace(" ", "")
    expr = re.sub(r"(\d)([a-zA-Z])", r"\1*\2", expr)
    # Eliminar caracteres no válidos
    expr = expr.replace("∀i", "").replace("\r", "").replace("\n", "")
    # Reemplazar variables como x1, x2 por x, y
    expr = expr.replace("x1", "x").replace("x2", "y")
    # Asegurar que los símbolos >= y <= sean consistentes (a veces OCR confunde)
    expr = expr.replace("≥", ">=").replace("≤", "<=")
    #elimina el 1 de mas
    expr =expr.replace("x11", "x1")
    expr= expr.replace("x12", "x2")
    expr= expr.replace("Max1", "Max")
    #por si acaso todavia no implemento minimizar z
    expr= expr.replace("Min1", "Min")
    return expr

def parse_funcion_objetivo(linea):#(lo pasa a sympy)
    expr = limpiar_expresion(linea.split("=")[1].strip())
    expr = expr.replace('x1', 'x').replace('x2', 'y')#desde el front recibe x1 y x2 a x,y esto esta en veremos ya lo probe pero hay errores:.replace('×1','x').replace('×2','y').replace(" ", "").replace("2=","Z=")
    return sp.sympify(expr)

def parse_restricciones(lista):#limpia las restricciones
    restricciones = []
    for l in lista:
        l = limpiar_expresion(l)
        l = l.replace('x1', 'x').replace('x2', 'y')#.replace('×1','x').replace('×2','y')..replace(" ", "").replace("2=","Z=")
        if "<=" in l:
            izq, der = l.split("<=")
            restricciones.append(sp.Le(sp.sympify(izq), sp.sympify(der)))
        elif ">=" in l:
            izq, der = l.split(">=")
            restricciones.append(sp.Ge(sp.sympify(izq), sp.sympify(der)))
        elif "=" in l:
            izq, der = l.split("=")
            restricciones.append(sp.Eq(sp.sympify(izq), sp.sympify(der)))
    return restricciones
'''
def reemplazar_variables_para_mostrar(expresion):
    expresion= expresion.replace("x11", "x1")
    expresion= expresion.replace("x12", "x2")
    return expresion
'''

#en maximizar...21-05-2025
def intersecciones_validas(restrs):
    puntos = []
    explicaciones = []
    for r1, r2 in combinations(restrs, 2):
        try:
            eq1 = sp.Eq(r1.lhs, r1.rhs)
            eq2 = sp.Eq(r2.lhs, r2.rhs)
            sol = sp.solve([eq1, eq2], (x, y), dict=True)
            if sol:
                punto = sol[0]
                px, py = punto[x], punto[y]
                if all(restr.subs({x: px, y: py}) for restr in restrs):
                    puntos.append((float(px), float(py)))
                    explicacion = f"   Intersección de {sp.pretty(eq1)} y {sp.pretty(eq2)}\n"
                    explicacion += f"   Resultado: x = {px}, y = {py}"
                    explicaciones.append(explicacion)
        except:
            continue
    return puntos, explicaciones

def intersecciones_con_ejes(restr):
    puntos = []
    desarrollo = ""
    eq = sp.Eq(restr.lhs, restr.rhs)
    try:
        px = sp.solve(eq.subs(y, 0), x)
        if px:
            desarrollo += f"   Si y = 0 → {eq.subs(y, 0)} ⇒ x = {px[0]} → Punto ({px[0]}, 0)\n"
            puntos.append((float(px[0]), 0))
    except:
        pass
    try:
        py = sp.solve(eq.subs(x, 0), y)
        if py:
            desarrollo += f"   Si x = 0 → {eq.subs(x, 0)} ⇒ y = {py[0]} → Punto (0, {py[0]})\n"
            puntos.append((0, float(py[0])))
    except:
        pass
    return puntos, desarrollo

#este ha de ser general
def generar_grafica(indice_paso,restricciones,vertices,mejor_punto):
    x_vals = np.linspace(0, 10, 400)
    fig, ax = plt.subplots(figsize=(5.5, 4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid(True)
    ax.set_title("Representación gráfica")

    if indice_paso >= 1:
        for i, restr in enumerate(restricciones):
            eq = sp.Eq(restr.lhs, restr.rhs)
            if y in eq.free_symbols:
                sol_y = sp.solve(eq, y)
                if sol_y:
                    f_y = sp.lambdify(x, sol_y[0], modules=["numpy"])
                    y_vals = f_y(x_vals)
                    ax.plot(x_vals, y_vals, label=f"Restricción {i+1}")
            elif x in eq.free_symbols:
                sol_x = sp.solve(eq, x)
                if sol_x:
                    ax.axvline(x=float(sol_x[0]), linestyle='--', label=f"x = {float(sol_x[0]):.2f}")

    if indice_paso >= 2:
        X, Y = np.meshgrid(x_vals, x_vals)
        Z = np.ones_like(X, dtype=bool)
        for restr in restricciones:
            expr = restr.lhs - restr.rhs
            f = sp.lambdify((x, y), expr, modules=["numpy"])
            if isinstance(restr, (sp.LessThan, sp.StrictLessThan)):
                Z &= f(X, Y) <= 0
            elif isinstance(restr, (sp.GreaterThan, sp.StrictGreaterThan)):
                Z &= f(X, Y) >= 0
            elif isinstance(restr, sp.Equality):
                Z &= np.isclose(f(X, Y), 0, atol=1e-3)
        ax.contourf(X, Y, Z, levels=[0.5, 1], colors=["skyblue"], alpha=0.5)

    if indice_paso >= 4:
        for px, py in vertices:
            ax.plot(px, py, "ro")
            ax.text(px + 0.1, py + 0.1, f"({round(px,1)},{round(py,1)})")

    if indice_paso >= 5:
        opt_x, opt_y = mejor_punto[0]
        ax.plot(opt_x, opt_y, "go", markersize=10, label="Óptimo")

    ax.legend(fontsize=7)
    buffer = io.BytesIO()
    canvas = FigureCanvas(fig)
    canvas.print_png(buffer)
    plt.close(fig)
    return buffer.getvalue()

#mostrar pasos
def paso_actual(request):
    pasos = request.session.get("pasos_generados", [])
    indice = request.session.get("indice_paso", 0)

    if pasos:
        paso = pasos[indice]
    else:
        paso = "No hay pasos disponibles"

    return JsonResponse({
        "paso": paso,
        "indice": indice,
        "total": len(pasos)
    })

def siguiente_paso(request):
    pasos = request.session.get("pasos_generados", [])
    indice = request.session.get("indice_paso", 0)

    if pasos:
        indice = min(indice + 1, len(pasos) - 1)
        request.session["indice_paso"] = indice

    return paso_actual(request)

def paso_anterior(request):
    indice = request.session.get("indice_paso", 0)
    indice = max(indice - 1, 0)
    request.session["indice_paso"] = indice

    return paso_actual(request)

@csrf_exempt
def ver_paso(request):#esto vamos a probarlo se supone que usa los datos guardados en request para mana
    indice = int(request.GET.get("paso", 0))
    pasos_generados = request.session.get("pasos_generados", [])
    if not pasos_generados:
        return HttpResponse("No hay pasos guardados en la sesión.")
    if indice < 0: indice = 0
    if indice >= len(pasos_generados): indice = len(pasos_generados) - 1
  
    # Recuperar datos serializados
    restricciones= pickle.loads(base64.b64decode(request.session["restricciones"]))#cambie el nombre de la variable pero la logica es la misma
    vertices = pickle.loads(base64.b64decode(request.session["vertices"]))
    mejor_punto = pickle.loads(base64.b64decode(request.session["mejor_punto"]))
    
    paso=pasos_generados[indice]
    #generar la grafica del paso actual
    grafica_bytes = generar_grafica(indice, restricciones, vertices, mejor_punto)
    grafica_base64 = base64.b64encode(grafica_bytes).decode()
    #grafica = generar_grafica(indice)
    #grafica_base64 = f"data:image/png;base64,{grafica.encode('base64').decode()}"

    return render(request, "funciones/pasos.html", {
        "indice": indice,
        "paso": paso,#pasos_generados[indice],#(esto estaba antes)
        "grafica_base64":  f"data:image/png;base64,{grafica_base64}",#grafica_base64,
        "tiene_anterior": indice > 0,
        "tiene_siguiente": indice < len(pasos_generados) - 1,
    })

@csrf_exempt
def maximizar(request):#Metodo Simplex maximizar
    if request.method == 'POST' and request.POST.getlist('item'):
        problema = request.POST.getlist('item')#NO TENIA EL POST
       
        print("")
        funcion_objetivo = parse_funcion_objetivo(problema[0])#limpia la funcion objetivo y la guarda en una variable
        restr_lines = [line for line in problema if any(op in line for op in ["<=", ">=", "="]) and "Z" not in line]#se asegurran que no este la funcion objetivo
        restricciones = parse_restricciones(restr_lines)#lo mismo
        
        vertices = []
        paso2_info = "2. Graficar restricciones:\nRepresentamos gráficamente las restricciones como rectas:\n"
        for restr in restricciones:
            eq = sp.Eq(restr.lhs, restr.rhs)
            puntos, desarrollo = intersecciones_con_ejes(restr)
            paso2_info += f"- {sp.pretty(eq)}\n{desarrollo}"
            for p in puntos:
                if all(restr.subs({x: p[0], y: p[1]}) for restr in restricciones):
                    vertices.append(p)

        inter_puntos, explicaciones = intersecciones_validas(restricciones)
        vertices += inter_puntos
        vertices = list(set(vertices))  # Quitar duplicados
        print("Vértices encontrados:", vertices)
        print("Restricciones:", restricciones)
        print("Puntos candidatos:", puntos)

        evaluaciones = []
        evaluacion_texto = ""
        for p in vertices:
            z_val = funcion_objetivo.subs({x: p[0], y: p[1]})
            evaluacion_texto += f"Z({p[0]},{p[1]}) = 3({p[0]}) + 5({p[1]}) = {3*p[0]} + {5*p[1]} = {z_val}\n"
            evaluaciones.append((p, z_val))

        mejor_punto = max(evaluaciones, key=lambda item: item[1])
        
        pasos_generados = []
       
        pasos_generados.append(
            f"1. Planteamiento del problema:\n{problema[0]}\n{problema[1]}\n" + "\n".join(problema[2:])
        )
        pasos_generados.append(paso2_info)

        pasos_generados.append(
            "3. Encontrar los vértices de la región factible:\n"
            "Marcamos la región que cumple con todas las restricciones incluyendo x, y ≥ 0.\n"
            "Sombreamos el área válida en la gráfica."
        )

        pasos_generados.append(
            "4. Calcular intersección entre restricciones:\nUsamos el método algebraico para resolver las ecuaciones:\n" +
            "\n".join(explicaciones)
        )

        pasos_generados.append(
            "5. Vértices factibles encontrados:\nSon aquellos puntos dentro de la gráfica\n" + ", ".join([f"({round(p[0],2)}, {round(p[1],2)})" for p in vertices])
        + "\nEvaluamos cada uno en Z")

        pasos_generados.append(
            "6. Evaluación en la función objetivo:\n" + evaluacion_texto +
            f"\nLa solución óptima es Z = {mejor_punto[1]} en el punto {mejor_punto[0]}"
        )

        pasos_generados.append(
            f"7. Conclusión:\nLa solución óptima se encuentra en el punto {mejor_punto[0]}, "
            f"donde Z alcanza su valor máximo de {mejor_punto[1]}. \n Este es el resultado mediante el método gráfico y tambien mediante programación lineal."
        )

        #problema_para_mostrar = [reemplazar_variables_para_mostrar(p) for p in pasos_generados]


       #guardar datos en request session
        request.session["pasos_generados"] = pasos_generados #problema_para_mostrar
        request.session["restricciones"] = base64.b64encode(pickle.dumps(restricciones)).decode()#este es nuevo
        request.session["vertices"] = base64.b64encode(pickle.dumps(vertices)).decode()
        request.session["mejor_punto"] = base64.b64encode(pickle.dumps(mejor_punto)).decode()

        return redirect("ver_paso")  # Asegúrate de tener una URL que apunte a esta vista
#prueba
@csrf_exempt
def resolver_ecuacion(request):#hay una plantilla en html que llama a esta por ahora voy a desviarla a otro lado
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