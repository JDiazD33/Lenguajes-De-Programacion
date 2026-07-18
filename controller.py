"""Modulo controlador: Flujo imperativo/OOP de la aplicacion web.

Paradigma imperativo / OOP:
- Clases del dominio: Revista (con herencia), CriterioBusqueda, ResultadoRecomendacion.
- Herencia y polimorfismo: RevistaOpenAccess y RevistaPremium extienden Revista
  con comportamiento diferenciado (descripcion_acceso, factor_accesibilidad).
- Encapsulamiento: atributos privados con @property (getters controlados).
- Factory method: crear_revista() instancia la subclase correcta.
- Value Object: CriterioBusqueda encapsula y valida las preferencias.
- Clase SistemaRecomendacion: orquesta la tuberia multiparadigma.
- Manejo del ciclo request-response web (rutas, formularios).
- Coordinacion de los otros modulos (logic_rules, processor) como
  pasos imperativos dentro del flujo.
"""

from flask import Blueprint, render_template, request
from logic_rules import aplicar_reglas, obtener_areas_disponibles
from processor import rankear_revistas
from datetime import datetime
from typing import Dict, List, Any, Optional


# ============================================================
# CLASES DEL DOMINIO (OOP)
# ============================================================

class Revista:
    """Entidad del dominio que representa una revista academica.

    Principios OOP demostrados:
    - ENCAPSULAMIENTO: atributos privados (_nombre, _area, etc.)
      con acceso controlado via @property (solo lectura).
    - ABSTRACCION: oculta la representacion interna y expone
      una interfaz limpia (to_dict, from_dict, __repr__).
    - CLASE BASE para herencia: RevistaOpenAccess y RevistaPremium.
    """

    def __init__(
        self,
        nombre: str,
        area: str,
        indexacion: str,
        apc: str,
        tiempo_revision: int,
        factor_impacto: float,
    ):
        """Inicializa una revista con sus atributos encapsulados.

        Args:
            nombre: nombre completo de la revista.
            area: area tematica principal.
            indexacion: nivel de indexacion (scopus q1, scielo, etc.).
            apc: si cobra APC ('si' o 'no').
            tiempo_revision: meses promedio de revision.
            factor_impacto: factor de impacto numerico.
        """
        self._nombre = nombre
        self._area = area
        self._indexacion = indexacion
        self._apc = apc
        self._tiempo_revision = tiempo_revision
        self._factor_impacto = factor_impacto

    # --- Properties (encapsulamiento con acceso de solo lectura) ---

    @property
    def nombre(self) -> str:
        """Nombre completo de la revista."""
        return self._nombre

    @property
    def area(self) -> str:
        """Area tematica principal."""
        return self._area

    @property
    def indexacion(self) -> str:
        """Nivel de indexacion."""
        return self._indexacion

    @property
    def apc(self) -> str:
        """Indica si cobra APC ('si' o 'no')."""
        return self._apc

    @property
    def tiempo_revision(self) -> int:
        """Meses promedio de revision."""
        return self._tiempo_revision

    @property
    def factor_impacto(self) -> float:
        """Factor de impacto numerico."""
        return self._factor_impacto

    # --- Metodos de conversion ---

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Revista":
        """Factory method: crea una Revista desde un diccionario.

        Args:
            data: dict con las claves nombre, area, indexacion, etc.

        Returns:
            Instancia de Revista.
        """
        return cls(
            nombre=data["nombre"],
            area=data["area"],
            indexacion=data["indexacion"],
            apc=data["apc"],
            tiempo_revision=data["tiempo_revision"],
            factor_impacto=data["factor_impacto"],
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convierte la revista a diccionario.

        Returns:
            Dict con todos los atributos de la revista.
        """
        return {
            "nombre": self._nombre,
            "area": self._area,
            "indexacion": self._indexacion,
            "apc": self._apc,
            "tiempo_revision": self._tiempo_revision,
            "factor_impacto": self._factor_impacto,
        }

    def descripcion_acceso(self) -> str:
        """Describe el tipo de acceso de la revista.

        Metodo base que las subclases sobreescriben (polimorfismo).

        Returns:
            Descripcion del tipo de acceso.
        """
        return "Acceso estandar"

    def calcular_factor_accesibilidad(self) -> float:
        """Calcula un factor de accesibilidad [0.0, 1.0].

        Metodo base para polimorfismo. Las subclases retornan
        valores distintos segun su tipo de acceso.

        Returns:
            Factor de accesibilidad normalizado.
        """
        return 0.5

    def __repr__(self) -> str:
        return (
            f"Revista('{self._nombre}', area='{self._area}', "
            f"FI={self._factor_impacto})"
        )

    def __str__(self) -> str:
        return f"{self._nombre} ({self._area})"


class RevistaOpenAccess(Revista):
    """Subclase: revista sin cargos de publicacion (APC = no).

    Demuestra HERENCIA (extiende Revista) y POLIMORFISMO
    (sobreescribe descripcion_acceso y calcular_factor_accesibilidad).
    """

    def descripcion_acceso(self) -> str:
        """Polimorfismo: retorna descripcion especifica para open access."""
        return "Publicacion gratuita (sin APC)"

    def calcular_factor_accesibilidad(self) -> float:
        """Polimorfismo: acceso abierto => maxima accesibilidad."""
        return 1.0 


class RevistaPremium(Revista):
    """Subclase: revista con cargos de publicacion (APC = si).

    Demuestra POLIMORFISMO: misma interfaz, comportamiento distinto.
    """

    def descripcion_acceso(self) -> str:
        """Polimorfismo: retorna descripcion especifica para premium."""
        return "Requiere pago de APC (Article Processing Charge)"

    def calcular_factor_accesibilidad(self) -> float:
        """Polimorfismo: acceso de pago => accesibilidad reducida."""
        return 0.7 





# ============================================================
# VALUE OBJECT: CRITERIOS DE BUSQUEDA
# ============================================================

class CriterioBusqueda:
    """Value Object que encapsula y valida las preferencias del usuario.

    Principios OOP:
    - ENCAPSULAMIENTO: datos validados en el constructor.
    - RESPONSABILIDAD UNICA: solo maneja criterios de busqueda.
    - FACTORY METHOD: from_form() crea instancias desde datos HTTP.
    - INMUTABILIDAD: una vez creado, los criterios no cambian.
    """

    def __init__(
        self,
        area: str = "",
        indexacion: str = "",
        apc: str = "",
        tiempo_max: str = "",
        impacto_min: str = "",
        palabras_clave: str = "",
        titulo: str = "",
        resumen: str = "",
    ):
        """Inicializa y normaliza los criterios de busqueda.

        Args:
            area: area tematica preferida.
            indexacion: nivel de indexacion deseado.
            apc: preferencia de APC ('si', 'no', o vacio).
            tiempo_max: tiempo maximo de revision (string).
            impacto_min: factor de impacto minimo (string).
            palabras_clave: keywords separadas por coma.
            titulo: titulo del articulo del investigador.
            resumen: resumen (abstract) del articulo del investigador.
        """
        self._area = area.strip().lower() if area else ""
        self._indexacion = indexacion.strip().lower() if indexacion else ""
        self._apc = apc.strip().lower() if apc else ""
        self._tiempo_max = tiempo_max.strip() if tiempo_max else ""
        self._impacto_min = impacto_min.strip() if impacto_min else ""
        self._palabras_clave = palabras_clave.strip() if palabras_clave else ""
        # El titulo y resumen se conservan sin normalizar a minusculas para
        # poder mostrarlos legibles en la interfaz; el processor se encarga
        # de normalizarlos al extraer los terminos relevantes.
        self._titulo = titulo.strip() if titulo else ""
        self._resumen = resumen.strip() if resumen else ""

    @classmethod
    def from_form(cls, form_data) -> "CriterioBusqueda":
        """Factory method: crea CriterioBusqueda desde datos del formulario.

        Patron Factory Method: encapsula la logica de construccion
        a partir de datos HTTP (request.form).

        Args:
            form_data: objeto request.form de Flask (ImmutableMultiDict).

        Returns:
            Instancia de CriterioBusqueda normalizada.
        """
        return cls(
            area=form_data.get("area", ""),
            indexacion=form_data.get("indexacion", ""),
            apc=form_data.get("apc", ""),
            tiempo_max=form_data.get("tiempo_max", ""),
            impacto_min=form_data.get("impacto_min", ""),
            palabras_clave=form_data.get("palabras_clave", ""),
            titulo=form_data.get("titulo", ""),
            resumen=form_data.get("resumen", ""),
        )

    def to_dict(self) -> Dict[str, str]:
        """Convierte los criterios a diccionario para los otros modulos.

        Returns:
            Dict con todos los criterios como strings.
        """
        return {
            "area": self._area,
            "indexacion": self._indexacion,
            "apc": self._apc,
            "tiempo_max": self._tiempo_max,
            "impacto_min": self._impacto_min,
            "palabras_clave": self._palabras_clave,
            "titulo": self._titulo,
            "resumen": self._resumen,
        }

    @property
    def area(self) -> str:
        return self._area

    @property
    def indexacion(self) -> str:
        return self._indexacion

    @property
    def apc(self) -> str:
        return self._apc

    @property
    def palabras_clave(self) -> str:
        return self._palabras_clave

    @property
    def titulo(self) -> str:
        """Titulo del articulo del investigador."""
        return self._titulo

    @property
    def resumen(self) -> str:
        """Resumen (abstract) del articulo del investigador."""
        return self._resumen

    def __repr__(self) -> str:
        return (
            f"CriterioBusqueda(area='{self._area}', "
            f"idx='{self._indexacion}', apc='{self._apc}')"
        )


# ============================================================
# RESULTADO DE RECOMENDACION
# ============================================================

class ResultadoRecomendacion:
    """Encapsula el resultado completo de una recomendacion.

    Principios OOP:
    - ENCAPSULAMIENTO: calcula estadisticas internamente.
    - PRINCIPIO DE MENOR CONOCIMIENTO: expone solo lo necesario.
    - RESPONSABILIDAD UNICA: solo gestiona datos de resultado.
    """

    def __init__(
        self,
        criterios: CriterioBusqueda,
        revistas_recomendadas: List[Dict[str, Any]],
        timestamp: str,
    ):
        """Inicializa el resultado con los datos de la recomendacion.

        Args:
            criterios: criterios originales del usuario.
            revistas_recomendadas: lista de revistas rankeadas.
            timestamp: marca temporal de la consulta.
        """
        self._criterios = criterios
        self._revistas = revistas_recomendadas
        self._timestamp = timestamp

    @property
    def revistas(self) -> List[Dict[str, Any]]:
        """Retorna copia de la lista de revistas (inmutabilidad)."""
        return list(self._revistas)

    @property
    def total(self) -> int:
        """Numero total de revistas recomendadas."""
        return len(self._revistas)

    @property
    def tiene_resultados(self) -> bool:
        """Indica si hay al menos una revista recomendada."""
        return len(self._revistas) > 0

    @property
    def estadisticas(self) -> Dict[str, Any]:
        """Calcula estadisticas del conjunto de resultados.

        Encapsula la logica de calculo de metricas: total,
        promedio y maximo de puntaje. El consumidor no necesita
        saber como se calculan.

        Returns:
            Dict con total_candidatos, promedio_puntaje, max_puntaje.
        """
        if not self._revistas:
            return {
                "total_candidatos": 0,
                "promedio_puntaje": 0,
                "max_puntaje": 0,
            }
        return {
            "total_candidatos": len(self._revistas),
            "promedio_puntaje": round(
                sum(r["puntaje_total"] for r in self._revistas)
                / len(self._revistas),
                4,
            ),
            "max_puntaje": round(
                max(r["puntaje_total"] for r in self._revistas), 4
            ),
        }

    def to_historial_entry(self) -> Dict[str, Any]:
        """Convierte el resultado a una entrada de historial.

        Returns:
            Dict formateado para almacenamiento en historial.
        """
        return {
            "preferencias": self._criterios.to_dict(),
            "total_candidatos": self.total,
            "top_resultados": [
                (r["nombre"], r["puntaje_total"])
                for r in self._revistas[:5]
            ],
            "timestamp": self._timestamp,
            "mensaje": (
                None
                if self.tiene_resultados
                else "NINGUNA revista cumple los criterios estrictos."
            ),
        }

    def __repr__(self) -> str:
        return f"ResultadoRecomendacion({self.total} revistas)"


# ============================================================
# CLASE PRINCIPAL: SISTEMA DE RECOMENDACION (OOP)
# ============================================================

class SistemaRecomendacion:
    """Orquesta el proceso de recomendacion integrando los 3 paradigmas.

    Esta clase es el corazon del paradigma OOP en el sistema:
    - ENCAPSULAMIENTO: historial privado con acceso controlado.
    - METODO PRINCIPAL: recomendar() ejecuta la tuberia completa.
    - ESTADO MUTABLE: mantiene registro de consultas realizadas.
    - COORDINACION: conecta los modulos logico y funcional.

    FLUJO DE INTEGRACION MULTIPARADIGMA:
        1. [IMPERATIVO] Controller recibe datos del formulario web.
           CriterioBusqueda.from_form() valida y encapsula los datos.
        2. [LOGICO]    Controller llama a logic_rules.aplicar_reglas()
                       para filtrar candidatos por reglas estrictas
                       y enriquecer con etiquetas logicas derivadas.
        3. [FUNCIONAL] Controller pasa candidatos a processor.rankear_revistas()
                       para calcular scores via pipeline funcional.
        4. [IMPERATIVO] Controller registra en historial (efecto secundario)
                       y renderiza la plantilla con ResultadoRecomendacion.
    """

    def __init__(self):
        """Inicializa el sistema con historial vacio."""
        self._historial: List[Dict[str, Any]] = []

    @property
    def historial(self) -> List[Dict[str, Any]]:
        """Retorna copia del historial (encapsulamiento)."""
        return list(self._historial)

    @property
    def total_consultas(self) -> int:
        """Numero total de consultas realizadas."""
        return len(self._historial)

    def recomendar(self, criterios: CriterioBusqueda) -> ResultadoRecomendacion:
        """Ejecuta la tuberia completa de recomendacion multiparadigma.

        Orquesta los tres paradigmas en secuencia:
        1. Logico  -> filtrado por reglas de inferencia.
        2. Funcional -> ranking por pipeline funcional.
        3. Imperativo -> registro en historial.

        Args:
            criterios: objeto CriterioBusqueda con las preferencias
                       del usuario validadas y normalizadas.

        Returns:
            ResultadoRecomendacion con las revistas rankeadas y
            sus estadisticas.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # --- PASO 1: FILTRADO LOGICO (logic_rules) ---
        # Se invoca el modulo de paradigma logico (kanren) para aplicar
        # reglas de inferencia y restricciones sobre la base de
        # conocimiento. Retorna revistas filtradas + etiquetas logicas.
        candidatos = aplicar_reglas(criterios.to_dict())

        if not candidatos:
            resultado = ResultadoRecomendacion(criterios, [], timestamp)
            self._historial.append(resultado.to_historial_entry())
            return resultado

        # --- PASO 2: RANKING FUNCIONAL (processor) ---
        # Se invoca el modulo de paradigma funcional (compose, partial,
        # map, filter, reduce, lambdas, lru_cache) para calcular
        # puntajes y ordenar por relevancia.
        revistas_rankeadas = rankear_revistas(candidatos, criterios.to_dict())

        # --- PASO 3: REGISTRO IMPERATIVO (controller) ---
        # Se modifica el estado interno (historial) como efecto
        # secundario del flujo imperativo.
        resultado = ResultadoRecomendacion(
            criterios, revistas_rankeadas, timestamp
        )
        self._historial.append(resultado.to_historial_entry())

        return resultado

    def obtener_ultimo_resultado(self) -> Optional[Dict[str, Any]]:
        """Retorna la ultima entrada del historial.

        Returns:
            Ultima consulta registrada, o None si no hay historial.
        """
        if not self._historial:
            return None
        return self._historial[-1]

    def limpiar_historial(self) -> None:
        """Limpia todo el historial de consultas."""
        self._historial.clear()


# ============================================================
# INSTANCIA GLOBAL Y RUTAS FLASK
# ============================================================

sistema = SistemaRecomendacion()
main_bp = Blueprint("main", __name__)


@main_bp.route("/", methods=["GET", "POST"])
def index():
    """Ruta principal: formulario de busqueda y visualizacion de resultados.

    GET:  Muestra el formulario vacio con estado inicial.
    POST: Procesa el formulario usando la tuberia multiparadigma:
          1. Crea CriterioBusqueda desde el formulario (OOP).
          2. Ejecuta sistema.recomendar() (OOP + Logico + Funcional).
          3. Extrae datos del ResultadoRecomendacion (OOP).
          4. Renderiza la plantilla con los resultados.

    Returns:
        HTML renderizado con la plantilla index.html.
    """
    resultados: List[Dict[str, Any]] = []
    preferencias: Dict[str, str] = {}
    estadisticas: Dict[str, Any] = {}

    if request.method == "POST":
        # Construccion OOP: CriterioBusqueda.from_form (factory method)
        criterios = CriterioBusqueda.from_form(request.form)
        preferencias = criterios.to_dict()

        # Tuberia multiparadigma: logico -> funcional -> registro
        resultado = sistema.recomendar(criterios)

        # Extraer datos del ResultadoRecomendacion (encapsulamiento)
        resultados = resultado.revistas
        estadisticas = resultado.estadisticas

    return render_template(
        "index.html",
        resultados=resultados,
        preferencias=preferencias,
        estadisticas=estadisticas,
        total_consultas=sistema.total_consultas,
        areas_disponibles=obtener_areas_disponibles(),
    )
