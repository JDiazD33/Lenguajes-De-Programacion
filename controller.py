"""Modulo controlador: Flujo imperativo/OOP de la aplicacion web.

Paradigma imperativo / OOP:
- Clase SistemaRecomendacion: encapsula estado (historial de consultas)
  y comportamiento (metodo recomendar que coordina los 3 modulos).
- Metodos con efectos secundarios: modifican self.historial.
- Secuencia explicita de pasos: 1) Logico -> 2) Funcional -> 3) Registro.
- Manejo del ciclo request-response web (rutas, formularios, redireccion).
- Coordinacion de los otros modulos (logic_rules, processor) como
  pasos imperativos dentro del flujo.
"""

from flask import Blueprint, render_template, request
from logic_rules import aplicar_reglas
from processor import rankear_revistas
from datetime import datetime


# ============================================================
# CLASE PRINCIPAL (OOP)
# ============================================================

class SistemaRecomendacion:
    """Orquesta el proceso de recomendacion integrando los 3 paradigmas.

    Esta clase es el corazon del paradigma OOP en el sistema:
    - Encapsula el estado (historial de consultas del usuario).
    - Expone un metodo recomendar() que ejecuta la tuberia completa.
    - Mantiene registro mutable de las consultas realizadas.

    FLUJO DE INTEGRACION MULTIPARADIGMA:
        1. [IMPERATIVO] Controller recibe datos del formulario web.
        2. [LOGICO]    Controller llama a logic_rules.aplicar_reglas()
                       para filtrar candidatos por reglas estrictas.
        3. [FUNCIONAL] Controller pasa candidatos a processor.rankear_revistas()
                       para calcular scores y ordenar.
        4. [IMPERATIVO] Controller registra la consulta en el historial
                       y renderiza la plantilla con los resultados.
    """

    def __init__(self):
        """Inicializa el sistema con historial vacio."""
        self.historial = []

    def recomendar(self, preferencias):
        """Ejecuta la tuberia completa de recomendacion multiparadigma.

        Args:
            preferencias (dict): datos del formulario con claves:
                - area, palabras_clave, indexacion, apc,
                  tiempo_max, impacto_min.

        Returns:
            list[dict]: revistas rankeadas y enriquecidas con puntajes.
        """
        # --- PASO 1: FILTRADO LOGICO (logic_rules) ---
        # Se invoca el modulo de paradigma logico (kanren) para aplicar
        # reglas de inferencia y restricciones duras sobre la base de
        # conocimiento. Retorna solo las revistas que cumplen
        # estrictamente los criterios del usuario.
        candidatos = aplicar_reglas(preferencias)

        if not candidatos:
            self.historial.append({
                "preferencias": dict(preferencias),
                "total_candidatos": 0,
                "top_resultados": [],
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "mensaje": "NINGUNA revista cumple los criterios estrictos."
            })
            return []

        # --- PASO 2: RANKING FUNCIONAL (processor) ---
        # Se invoca el modulo de paradigma funcional (map, filter,
        # reduce, lambdas) para calcular puntajes de coincidencia
        # y ordenar las revistas de mayor a menor relevancia.
        resultados = rankear_revistas(candidatos, preferencias)

        # --- PASO 3: REGISTRO IMPERATIVO (controller) ---
        # Se modifica el estado interno (historial) como efecto
        # secundario del flujo imperativo de la aplicacion.
        self.historial.append({
            "preferencias": dict(preferencias),
            "total_candidatos": len(candidatos),
            "top_resultados": [
                (r["nombre"], r["puntaje_total"]) for r in resultados[:5]
            ],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "mensaje": None
        })

        return resultados


# ============================================================
# INSTANCIA GLOBAL Y RUTAS FLASK
# ============================================================

sistema = SistemaRecomendacion()
main_bp = Blueprint("main", __name__)


@main_bp.route("/", methods=["GET", "POST"])
def index():
    """Ruta principal: formulario de busqueda y visualizacion de resultados.

    GET:  Muestra el formulario vacio.
    POST: Procesa el formulario, ejecuta la tuberia de recomendacion y
          muestra los resultados en la misma pagina.

    Returns:
        str: HTML renderizado con la plantilla index.html.
    """
    resultados = []
    preferencias = {}
    estadisticas = {}

    if request.method == "POST":
        # Recepcion imperativa de datos del formulario
        preferencias = {
            "area": request.form.get("area", "").strip().lower(),
            "palabras_clave": request.form.get("palabras_clave", "").strip(),
            "indexacion": request.form.get("indexacion", "").strip().lower(),
            "apc": request.form.get("apc", "").strip().lower(),
            "tiempo_max": request.form.get("tiempo_max", "").strip(),
            "impacto_min": request.form.get("impacto_min", "").strip(),
        }

        # Ejecutar tuberia multiparadigma
        resultados = sistema.recomendar(preferencias)

        # Calcular estadisticas para mostrar en la interfaz
        estadisticas = {
            "total_candidatos": len(resultados),
            "promedio_puntaje": (
                round(
                    sum(r["puntaje_total"] for r in resultados) / len(resultados),
                    4,
                )
                if resultados
                else 0
            ),
            "max_puntaje": (
                round(max(r["puntaje_total"] for r in resultados), 4)
                if resultados
                else 0
            ),
        }

    return render_template(
        "index.html",
        resultados=resultados,
        preferencias=preferencias,
        estadisticas=estadisticas,
        total_consultas=len(sistema.historial),
        areas_disponibles=[
            "multidisciplinaria",
            "ciencias de la computacion",
            "fisica",
            "ciencias ambientales",
            "linguistica",
            "bibliotecologia",
            "psicologia",
        ],
    )
