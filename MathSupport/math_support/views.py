#views.py solo maneja las vistas 
from django.shortcuts import render,redirect
from django.contrib import messages
from .db import UsuarioModel#esto es de la collection de usuarios
from .db import ProblemaModel #esto es de la collection de los problemas matematicos
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import io
from sympy import sympify, Eq
import sympy as sp
#ocr librerias
from pix2text import Pix2Text
from pylatexenc.latex2text import LatexNodes2Text
from PIL import Image
import os
from django.core.files.storage import FileSystemStorage
from django.conf import settings
#resolucion de problemas librerias
import matplotlib.pyplot as plt
import numpy as np
import re
from tkinter import *
from tkinter import messagebox
from itertools import combinations

'''
# funciones auxiliares
def extraer_objetivo_y_restricciones(texto):
    lineas = texto.split('\n')
    objetivo = ''
    restricciones = []
    for linea in lineas:
        if 'z' in linea.lower() and '=' in linea:
            objetivo = linea.split('=')[-1].strip()
        elif linea.strip():
            restricciones.append(linea.strip())
    return objetivo, restricciones
'''
#OCR
# Carga el modelo una sola vez
model = Pix2Text(model_name='mfr')#para ejercicios manuscritos
#19/05/2025
#esto funciona pero la no negatividad la pone despues de la funcion objetivo 
@csrf_exempt
def ocr_view(request):
    if request.method == 'POST' and request.FILES.getlist('images'):#recupera la lista de las imagenes ingresadas en el formulario
        files = request.FILES.getlist('images')#y las pasa a una lista
        resultados = []
       # objetivo_final = ""
       # restricciones_final = []

        for image_file in files:
            fs = FileSystemStorage()
            filename = fs.save(image_file.name, image_file)
            image_path = fs.path(filename)

            try:
                image = Image.open(image_path).convert('RGB')
                latex_result = model.recognize(image)
                texto_legible = LatexNodes2Text().latex_to_text(latex_result)
               # objetivo, restricciones = extraer_objetivo_y_restricciones(texto_legible)
                #texto_ordenado = limpiar_y_ordenar(texto_legible)
            except Exception as e:
                latex_result = "Error al procesar imagen"
                texto_legible = str(e) #eso estaba primero
                #texto_ordenado=str(e)
               # objetivo = ""
               # restricciones = []
            resultados.append({#esta
                'latex': latex_result,
                'texto': texto_legible, #eso estaba primero
                #'texto':texto_ordenado
               # 'objetivo': objetivo,
                #'restricciones': restricciones
            })

            os.remove(image_path)

        return render(request, 'funciones/result.html', {#result es en donde se muestra la ecuacion :b
            'resultados': resultados
        })

    return render(request, 'funciones/upload.html')

#resolucion de problemas (estamos en pruebas)
'''

def parse_func_obj(texto):
    coef = [0, 0]
    texto = texto.replace(' ', '').replace('-', '+-')
    partes = texto.split('+')
    for p in partes:
        if 'x' in p:
            coef[0] = int(p.replace('x', '') or '1')
        elif 'y' in p:
            coef[1] = int(p.replace('y', '') or '1')
    return coef

def parse_restriccion(linea):
    match = re.match(r'([\-0-9x+y\s]+)(<=|>=|=)([\-0-9]+)', linea.replace(' ', ''))
    if not match:
        raise ValueError(f"Restricción no válida: {linea}")
    izq, signo, der = match.groups()
    coef = [0, 0]
    izq = izq.replace('-', '+-')
    partes = izq.split('+')
    for p in partes:
        if 'x' in p:
            coef[0] = int(p.replace('x', '') or '1')
        elif 'y' in p:
            coef[1] = int(p.replace('y', '') or '1')
    der = int(der)
    pasos.append(f"Restricción original: {linea}")
    if signo == '>=':
        pasos.append(f"Transformamos '{linea}' a equivalente con '<=' al multiplicar por -1")
        coef = [-c for c in coef]
        der = -der
    elif signo == '=':
        pasos.append(f"Transformamos '{linea}' en dos restricciones: <= y >=")
        return [coef + [der], [-c for c in coef] + [-der]]
    return [coef + [der]]

def punto_valido(punto, restricciones):
    for r in restricciones:
        if np.dot(r[:2], punto) > r[2] + 1e-6:
            return False
    return True

def graficar():
    try:
        texto_funcion = entrada_funcion.get()
        restricciones_texto = entrada_restricciones.get("1.0", END).strip().splitlines()
        explicacion.delete("1.0", END)
        pasos.clear()

        if not texto_funcion or not restricciones_texto:
            raise ValueError("Falta la función o las restricciones")

        pasos.append(f"Función Objetivo: Z = {texto_funcion}")
        f_obj = parse_func_obj(texto_funcion)
        pasos.append(f"Coeficientes: {f_obj}")

        restricciones = []
        for r in restricciones_texto:
            partes = parse_restriccion(r)
            restricciones.extend(partes)

        restricciones = np.array(restricciones)

        x_vals = np.linspace(0, 20, 800)
        y_vals = np.linspace(0, 20, 800)
        x, y = np.meshgrid(x_vals, y_vals)
        puntos = np.c_[x.ravel(), y.ravel()]
        factibles = np.array([p for p in puntos if punto_valido(p, restricciones)])

        if factibles.size == 0:
            messagebox.showerror("Sin solución", "No hay región factible.")
            return

        pasos.append(f"Calculando región factible (todos los puntos que cumplen las restricciones)...")
        z = np.dot(factibles, f_obj)
        max_idx = np.argmax(z)
        max_punto = factibles[max_idx]
        max_val = z[max_idx]

        pasos.append(f"Punto óptimo encontrado en {tuple(max_punto)} con Z = {max_val:.2f}")

        # Mostrar pasos en interfaz
        explicacion.insert(END, "\n".join(pasos))

        # Graficar
        fig, ax = plt.subplots()
        for r in restricciones:
            a, b, c = r
            if b != 0:
                y_res = (c - a * x_vals) / b
                ax.plot(x_vals, y_res, label=f"{a}x + {b}y <= {c}")
            elif a != 0:
                x_res = c / a
                ax.axvline(x_res, label=f"x = {x_res}")

        ax.scatter(factibles[:, 0], factibles[:, 1], s=1, color='lightblue', label="Región Factible")
        ax.plot(max_punto[0], max_punto[1], 'ro', label=f"Máx Z = {max_val:.2f} en {tuple(max_punto)}")
        z_linea = (max_val - f_obj[0] * x_vals) / f_obj[1]
        ax.plot(x_vals, z_linea, '--', label=f"Z = {max_val:.2f}")

        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_title('Solución Gráfica - Maximización')
        ax.legend()
        plt.grid()
        plt.show()

    except Exception as e:
        messagebox.showerror("Error", str(e))

# Variables globales para mostrar pasos
pasos = []

# Interfaz
ventana = Tk()
ventana.title("Maximización paso a paso")
ventana.geometry("700x500")

Label(ventana, text="Función Objetivo (ej: 3x + 2y):").pack()
entrada_funcion = Entry(ventana, width=50)
entrada_funcion.pack()

Label(ventana, text="Restricciones (una por línea, ej: x + y <= 4):").pack()
entrada_restricciones = Text(ventana, height=8, width=50)
entrada_restricciones.pack()

Button(ventana, text="Graficar y Explicar", command=graficar).pack(pady=10)

Label(ventana, text="Explicación paso a paso:").pack()
explicacion = Text(ventana, height=10, width=80)
explicacion.pack()

ventana.mainloop()
'''
#20-05-2025

x, y = sp.symbols("x y")
variables = (x, y)

def limpiar_expresion(expr):#revisa que la expresion ingresada(lista) contenga una letra (como en la funcion objetivo usa Z como funcion (para maximizar))
    expr = expr.replace(" ", "")
    expr = re.sub(r"(\d)([a-zA-Z])", r"\1*\2", expr)
    return expr

def parse_funcion_objetivo(linea):#(lo pasa a sympy)
    expr = limpiar_expresion(linea.split("=")[1].strip())
    return sp.sympify(expr)


def parse_restricciones(lista):#limpia las restricciones
    restricciones = []
    for l in lista:
        l = limpiar_expresion(l)
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


@csrf_exempt
def maximizar(request):#Metodo Simplex maximizar
    if request.method == 'POST' and request.getlist('item'):
        problema = request.getlist('item')
       
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





#auxilio :')
'''

x, y = sp.symbols("x y")
variables = (x, y)

def limpiar_expresion(expr):#revisa que la expresion ingresada(lista) contenga una letra (como en la funcion objetivo usa Z como funcion (para maximizar))
    expr = expr.replace(" ", "")
    expr = re.sub(r"(\d)([a-zA-Z])", r"\1*\2", expr)
    return expr

def parse_funcion_objetivo(linea):#(lo pasa a sympy)
    expr = limpiar_expresion(linea.split("=")[1].strip())
    return sp.sympify(expr)

def parse_restricciones(lista):#limpia las restricciones
    restricciones = []
    for l in lista:
        l = limpiar_expresion(l)
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

funcion_objetivo = parse_funcion_objetivo(problema[0])#limpia la funcion objetivo y la guarda en una variable
restr_lines = [line for line in problema if any(op in line for op in ["<=", ">=", "="]) and "Z" not in line]#se asegurran que no este la funcion objetivo
restricciones = parse_restricciones(restr_lines)#lo mismo

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

evaluaciones = []
evaluacion_texto = ""
for p in vertices:
    z_val = funcion_objetivo.subs({x: p[0], y: p[1]})
    evaluacion_texto += f"Z({p[0]},{p[1]}) = 3({p[0]}) + 5({p[1]}) = {3*p[0]} + {5*p[1]} = {z_val}\n"
    evaluaciones.append((p, z_val))

mejor_punto = max(evaluaciones, key=lambda item: item[1])

# ======================= PARTE 2: PASOS DINÁMICOS =======================

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

'''






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