"""Modulo logico: Base de conocimiento y reglas de inferencia con kanren.

Paradigma logico:
- Define relaciones como hechos (facts) en una base de conocimiento declarativa.
- Utiliza la libreria kanren para consultas con variables logicas y unificacion.
- Implementa reglas de inferencia con conde (disyuncion logica / OR) y lall
  (conjuncion logica / AND).
- RELACIONES DERIVADAS: infiere propiedades complejas a partir de hechos
  base (alto_impacto, publicacion_rapida, acceso_abierto).  Estas relaciones
  NO estan explicitas en los datos originales; se deducen por inferencia.
- REGLAS COMPUESTAS: combina multiples relaciones derivadas para clasificar
  revistas como 'destacada', 'accesible' o 'emergente'.
- Separa el CONOCIMIENTO (que revistas existen y sus atributos) del
  CONTROL (como se filtran segun las preferencias del usuario).
"""

try:
    from kanren import Relation, facts, run, var, conde
    from kanren.core import lall
    KANREN_AVAILABLE = True
except ImportError:
    KANREN_AVAILABLE = False
    print("[logic_rules] kanren no disponible, se usara modo fallback.")

from typing import Dict, List, Any, Set


# ============================================================
# BASE DE CONOCIMIENTO: 10 revistas cientificas reales/realistas
# ============================================================

base_datos: List[Dict[str, Any]] = [
    {
        "nombre": "Nature",
        "area": "multidisciplinaria",
        "indexacion": "scopus q1",
        "apc": "si",
        "tiempo_revision": 6,
        "factor_impacto": 49.96,
    },
    {
        "nombre": "Science",
        "area": "multidisciplinaria",
        "indexacion": "scopus q1",
        "apc": "si",
        "tiempo_revision": 4,
        "factor_impacto": 47.73,
    },
    {
        "nombre": "IEEE Transactions on Pattern Analysis and Machine Intelligence",
        "area": "ciencias de la computacion",
        "indexacion": "scopus q1",
        "apc": "si",
        "tiempo_revision": 8,
        "factor_impacto": 24.31,
    },
    {
        "nombre": "Journal of Applied Physics",
        "area": "fisica",
        "indexacion": "scopus q2",
        "apc": "no",
        "tiempo_revision": 3,
        "factor_impacto": 2.87,
    },
    {
        "nombre": "Revista Mexicana de Fisica",
        "area": "fisica",
        "indexacion": "scielo",
        "apc": "no",
        "tiempo_revision": 4,
        "factor_impacto": 0.65,
    },
    {
        "nombre": "PLOS ONE",
        "area": "multidisciplinaria",
        "indexacion": "scopus q1",
        "apc": "si",
        "tiempo_revision": 3,
        "factor_impacto": 3.75,
    },
    {
        "nombre": "Journal of Cleaner Production",
        "area": "ciencias ambientales",
        "indexacion": "scopus q1",
        "apc": "si",
        "tiempo_revision": 7,
        "factor_impacto": 11.07,
    },
    {
        "nombre": "Boletin de Linguistica",
        "area": "linguistica",
        "indexacion": "scielo",
        "apc": "no",
        "tiempo_revision": 6,
        "factor_impacto": 0.25,
    },
    {
        "nombre": "Investigacion Bibliotecologica",
        "area": "bibliotecologia",
        "indexacion": "latindex",
        "apc": "no",
        "tiempo_revision": 4,
        "factor_impacto": 0.45,
    },
    {
        "nombre": "Revista Latinoamericana de Psicologia",
        "area": "psicologia",
        "indexacion": "latindex",
        "apc": "no",
        "tiempo_revision": 5,
        "factor_impacto": 0.82,
    },
]


# ============================================================
# RELACIONES LOGICAS BASE (hechos extensionales)
# ============================================================
# Los hechos extensionales son los datos "crudos" que se declaran
# directamente: cada revista TIENE una indexacion, un area, etc.

if KANREN_AVAILABLE:
    # --- Relaciones base (atributos directos) ---
    indexacion_rel = Relation()
    area_rel = Relation()
    apc_rel = Relation()

    # --- Relaciones DERIVADAS (inferidas desde los datos base) ---
    # Estas relaciones NO existen explicitamente en la base de datos.
    # Se deducen aplicando reglas sobre los atributos numericos.
    # Esto demuestra INFERENCIA LOGICA real: derivar conocimiento
    # nuevo a partir de hechos existentes.
    alto_impacto = Relation()        # factor_impacto >= 10.0
    medio_impacto = Relation()       # 1.0 <= factor_impacto < 10.0
    bajo_impacto = Relation()        # factor_impacto < 1.0
    publicacion_rapida = Relation()  # tiempo_revision <= 4 meses
    publicacion_moderada = Relation()  # 4 < tiempo_revision <= 6
    publicacion_lenta = Relation()   # tiempo_revision > 6 meses
    acceso_abierto = Relation()      # apc == "no"
    acceso_pago = Relation()         # apc == "si"

    for revista in base_datos:
        nombre = revista["nombre"]

        # Poblar hechos base (extensionales)
        facts(indexacion_rel, (nombre, revista["indexacion"]))
        facts(area_rel, (nombre, revista["area"]))
        facts(apc_rel, (nombre, revista["apc"]))

        # --- Inferir y poblar relaciones derivadas ---

        # Clasificacion por factor de impacto
        if revista["factor_impacto"] >= 10.0:
            facts(alto_impacto, (nombre,))
        elif revista["factor_impacto"] >= 1.0:
            facts(medio_impacto, (nombre,))
        else:
            facts(bajo_impacto, (nombre,))

        # Clasificacion por velocidad de revision
        if revista["tiempo_revision"] <= 4:
            facts(publicacion_rapida, (nombre,))
        elif revista["tiempo_revision"] <= 6:
            facts(publicacion_moderada, (nombre,))
        else:
            facts(publicacion_lenta, (nombre,))

        # Clasificacion por tipo de acceso
        if revista["apc"] == "no":
            facts(acceso_abierto, (nombre,))
        else:
            facts(acceso_pago, (nombre,))


# ============================================================
# REGLAS DE INFERENCIA COMPUESTAS (kanren)
# ============================================================
# Las reglas compuestas combinan multiples relaciones derivadas
# para inferir clasificaciones de nivel superior. Esto demuestra
# encadenamiento de reglas (chaining) propio del paradigma logico.

def regla_revista_destacada(x: var) -> Any:
    """Regla compuesta: una revista es 'destacada' si tiene alto impacto
    Y se publica en tiempo rapido o moderado.

    Demuestra: conjuncion (lall/AND) + disyuncion (conde/OR) anidadas.
    Esto es inferencia multi-nivel: se combinan dos relaciones derivadas.

    Equivalente en Prolog:
        destacada(X) :- alto_impacto(X), (publicacion_rapida(X) ; publicacion_moderada(X)).

    Args:
        x: variable logica kanren a unificar.

    Returns:
        Goal kanren que representa la regla.
    """
    return lall(
        alto_impacto(x),
        conde(
            [publicacion_rapida(x)],
            [publicacion_moderada(x)],
        ),
    )


def regla_revista_accesible(x: var) -> Any:
    """Regla compuesta: una revista es 'accesible' si tiene acceso abierto
    Y tiene al menos impacto medio o alto.

    Util para investigadores que buscan revistas sin costo con
    cierto nivel de prestigio.

    Equivalente en Prolog:
        accesible(X) :- acceso_abierto(X), (medio_impacto(X) ; alto_impacto(X)).

    Args:
        x: variable logica kanren a unificar.

    Returns:
        Goal kanren que representa la regla.
    """
    return lall(
        acceso_abierto(x),
        conde(
            [medio_impacto(x)],
            [alto_impacto(x)],
        ),
    )


def regla_revista_emergente(x: var) -> Any:
    """Regla compuesta: una revista es 'emergente' si tiene bajo impacto,
    acceso abierto Y publicacion rapida.

    Util para investigadores que buscan publicar rapidamente en
    revistas accesibles, aunque de menor prestigio.

    Equivalente en Prolog:
        emergente(X) :- bajo_impacto(X), acceso_abierto(X), publicacion_rapida(X).

    Args:
        x: variable logica kanren a unificar.

    Returns:
        Goal kanren que representa la regla.
    """
    return lall(
        bajo_impacto(x),
        acceso_abierto(x),
        publicacion_rapida(x),
    )


# ============================================================
# FUNCIONES DE CONSULTA LOGICA
# ============================================================

def consultar_destacadas() -> List[str]:
    """Consulta logica: obtiene todas las revistas destacadas.

    Ejecuta la regla compuesta regla_revista_destacada sobre toda
    la base de conocimiento mediante run(0, ...) (0 = sin limite).

    Returns:
        Lista de nombres de revistas que cumplen la regla.
    """
    if not KANREN_AVAILABLE:
        return [
            j["nombre"]
            for j in base_datos
            if j["factor_impacto"] >= 10.0 and j["tiempo_revision"] <= 6
        ]
    x = var()
    return list(run(0, x, regla_revista_destacada(x)))


def consultar_accesibles() -> List[str]:
    """Consulta logica: obtiene todas las revistas accesibles.

    Returns:
        Lista de nombres de revistas accesibles y con buen impacto.
    """
    if not KANREN_AVAILABLE:
        return [
            j["nombre"]
            for j in base_datos
            if j["apc"] == "no" and j["factor_impacto"] >= 1.0
        ]
    x = var()
    return list(run(0, x, regla_revista_accesible(x)))


def consultar_emergentes() -> List[str]:
    """Consulta logica: obtiene todas las revistas emergentes.

    Returns:
        Lista de nombres de revistas emergentes (bajo impacto, rapidas, abiertas).
    """
    if not KANREN_AVAILABLE:
        return [
            j["nombre"]
            for j in base_datos
            if j["factor_impacto"] < 1.0
            and j["apc"] == "no"
            and j["tiempo_revision"] <= 4
        ]
    x = var()
    return list(run(0, x, regla_revista_emergente(x)))


# ============================================================
# FUNCION DE ETIQUETADO LOGICO
# ============================================================

def _obtener_etiquetas_logicas(nombre: str) -> List[str]:
    """Obtiene las etiquetas logicas derivadas para una revista.

    Consulta las relaciones derivadas y las reglas compuestas
    para clasificar la revista.

    Args:
        nombre: nombre de la revista a clasificar.

    Returns:
        Lista de etiquetas semanticas inferidas.
    """
    etiquetas: List[str] = []

    # Etiquetas de impacto (derivadas)
    if nombre in set(consultar_destacadas()):
        etiquetas.append("Destacada")
    if nombre in set(consultar_accesibles()):
        etiquetas.append("Accesible")
    if nombre in set(consultar_emergentes()):
        etiquetas.append("Emergente")

    # Etiquetas de velocidad (derivadas de relaciones base)
    if KANREN_AVAILABLE:
        x = var()
        if list(run(0, x, lall(publicacion_rapida(x), lambda s: (s,) if s.get(x, None) == nombre else ()))):
            pass  # ya manejado por las reglas compuestas
    # Clasificacion simple basada en datos
    revista_data = next((j for j in base_datos if j["nombre"] == nombre), None)
    if revista_data:
        if revista_data["factor_impacto"] >= 10.0:
            etiquetas.append("Alto Impacto")
        elif revista_data["factor_impacto"] >= 1.0:
            etiquetas.append("Impacto Medio")

        if revista_data["tiempo_revision"] <= 4:
            etiquetas.append("Rapida")

    return etiquetas


# ============================================================
# FUNCION PRINCIPAL DE INFERENCIA LOGICA
# ============================================================

def aplicar_reglas(preferencias: Dict[str, str]) -> List[Dict[str, Any]]:
    """Aplica reglas logicas para filtrar revistas segun preferencias.

    Utiliza kanren para inferir que revistas cumplen estrictamente
    las condiciones definidas por el usuario.

    PARADIGMA LOGICO — flujo completo:
    1. Hechos base: atributos de cada revista como relaciones.
    2. Relaciones derivadas: alto_impacto, publicacion_rapida, etc.
    3. Reglas compuestas: destacada, accesible, emergente.
    4. Consultas: run() con variables logicas (var()) y goals.
    5. Conjuncion (AND): lall() para combinar goals.
    6. Disyuncion (OR): conde() para alternativas.
    7. Etiquetado: clasificacion inferida para cada resultado.

    Args:
        preferencias: dict con claves 'area', 'indexacion', 'apc',
                      'tiempo_max', 'impacto_min'.

    Returns:
        Lista de dicts de revistas que cumplen las reglas, enriquecidas
        con 'etiquetas_logicas' inferidas por el motor logico.
    """
    if not KANREN_AVAILABLE:
        return _filtrar_fallback(preferencias)

    x = var()
    idx_pref = preferencias.get("indexacion", "").strip().lower()
    area_pref = preferencias.get("area", "").strip().lower()
    apc_pref = preferencias.get("apc", "").strip().lower()

    # --- Construir goals base (AND logico) ---
    goals_base = []
    if idx_pref and idx_pref not in ("cualquier", ""):
        goals_base.append(indexacion_rel(x, idx_pref))
    if apc_pref and apc_pref not in ("cualquier", ""):
        goals_base.append(apc_rel(x, apc_pref))

    # --- Determinar nombres validos segun los filtros ---
    if not area_pref and not goals_base:
        # Sin filtros: todas las revistas son candidatas
        nombres_validos: Set[str] = set(j["nombre"] for j in base_datos)

    elif not area_pref and goals_base:
        # Solo filtros de indexacion/apc (sin area)
        nombres_validos = set(run(0, x, *goals_base))

    elif area_pref and not goals_base:
        # Solo filtro de area, con regla de ampliacion multidisciplinaria
        # conde expresa: area = area_pref OR area = "multidisciplinaria"
        regla_ampliacion = conde(
            [area_rel(x, area_pref)],
            [area_rel(x, "multidisciplinaria")],
        )
        nombres_validos = set(run(0, x, regla_ampliacion))

    else:
        # Area + otros filtros
        # Regla de conjuncion: area exacta + goals_base (AND)
        estrictos = set(run(0, x, area_rel(x, area_pref), *goals_base))
        # Regla de ampliacion: (area exacta OR multidisciplinaria) + goals_base
        regla_ampliacion = conde(
            [area_rel(x, area_pref)],
            [area_rel(x, "multidisciplinaria")],
        )
        ampliados = set(run(0, x, regla_ampliacion, *goals_base))
        nombres_validos = estrictos | ampliados

    # Reconstruir lista de dicts filtrada
    resultado = [j for j in base_datos if j["nombre"] in nombres_validos]

    # --- Filtros numericos adicionales ---
    try:
        tiempo_max = preferencias.get("tiempo_max", "")
        if tiempo_max:
            tmax = int(tiempo_max)
            resultado = [j for j in resultado if j["tiempo_revision"] <= tmax]

        impacto_min = preferencias.get("impacto_min", "")
        if impacto_min:
            imin = float(impacto_min)
            resultado = [j for j in resultado if j["factor_impacto"] >= imin]
    except (ValueError, TypeError):
        pass

    # --- Enriquecer con etiquetas logicas derivadas ---
    # Cada revista recibe etiquetas inferidas por las reglas compuestas
    # del motor logico (destacada, accesible, emergente, etc.)
    resultado_enriquecido = []
    for revista in resultado:
        etiquetas = _obtener_etiquetas_logicas(revista["nombre"])
        resultado_enriquecido.append({**revista, "etiquetas_logicas": etiquetas})

    return resultado_enriquecido


# ============================================================
# MODO FALLBACK (sin kanren)
# ============================================================

def _filtrar_fallback(preferencias: Dict[str, str]) -> List[Dict[str, Any]]:
    """Modo fallback cuando kanren no esta instalado.

    Implementa la misma semantica de filtrado con Python puro,
    incluyendo el etiquetado logico derivado.

    Args:
        preferencias: dict con criterios de busqueda.

    Returns:
        Lista de revistas filtradas con etiquetas logicas.
    """
    resultado = list(base_datos)

    idx_pref = preferencias.get("indexacion", "").strip().lower()
    area_pref = preferencias.get("area", "").strip().lower()
    apc_pref = preferencias.get("apc", "").strip().lower()

    if idx_pref and idx_pref != "cualquier":
        resultado = [j for j in resultado if j["indexacion"] == idx_pref]
    if area_pref:
        estrictos = [j for j in resultado if j["area"] == area_pref]
        ampliados = [j for j in resultado if j["area"] == "multidisciplinaria"]
        resultado = estrictos + [j for j in ampliados if j not in estrictos]
    if apc_pref and apc_pref != "cualquier":
        resultado = [j for j in resultado if j["apc"] == apc_pref]

    try:
        tiempo_max = preferencias.get("tiempo_max", "")
        if tiempo_max:
            tmax = int(tiempo_max)
            resultado = [j for j in resultado if j["tiempo_revision"] <= tmax]
        impacto_min = preferencias.get("impacto_min", "")
        if impacto_min:
            imin = float(impacto_min)
            resultado = [j for j in resultado if j["factor_impacto"] >= imin]
    except (ValueError, TypeError):
        pass

    # Enriquecer con etiquetas logicas (modo fallback)
    resultado_enriquecido = []
    for revista in resultado:
        etiquetas = _obtener_etiquetas_logicas(revista["nombre"])
        resultado_enriquecido.append({**revista, "etiquetas_logicas": etiquetas})

    return resultado_enriquecido


# ============================================================
# FUNCIONES AUXILIARES PUBLICAS
# ============================================================

def obtener_areas_disponibles() -> List[str]:
    """Retorna lista de areas tematicas disponibles.

    Returns:
        Areas unicas ordenadas alfabeticamente.
    """
    return sorted(set(j["area"] for j in base_datos))


def obtener_indexaciones_disponibles() -> List[str]:
    """Retorna lista de niveles de indexacion disponibles.

    Returns:
        Indexaciones unicas ordenadas alfabeticamente.
    """
    return sorted(set(j["indexacion"] for j in base_datos))
