"""Modulo logico: Base de conocimiento y reglas de inferencia con kanren.

Paradigma logico:
- Define relaciones como hechos (facts) en una base de conocimiento declarativa.
- Utiliza la libreria kanren para consultas con variables logicas y unificacion.
- Implementa reglas de inferencia con conde (disyuncion logica / OR).
- Separa el conocimiento (que revistas existen y sus atributos) del
  control (como se filtran segun las preferencias del usuario).
"""

try:
    from kanren import Relation, facts, run, var, conde
    KANREN_AVAILABLE = True
except ImportError:
    KANREN_AVAILABLE = False
    print("[logic_rules] kanren no disponible, se usara modo fallback.")

# ============================================================
# BASE DE CONOCIMIENTO: 10 revistas cientificas reales/realistas
# ============================================================

base_datos = [
    {
        "nombre": "Nature",
        "area": "multidisciplinaria",
        "indexacion": "scopus q1",
        "apc": "si",
        "tiempo_revision": 6,
        "factor_impacto": 49.96
    },
    {
        "nombre": "Science",
        "area": "multidisciplinaria",
        "indexacion": "scopus q1",
        "apc": "si",
        "tiempo_revision": 4,
        "factor_impacto": 47.73
    },
    {
        "nombre": "IEEE Transactions on Pattern Analysis and Machine Intelligence",
        "area": "ciencias de la computacion",
        "indexacion": "scopus q1",
        "apc": "si",
        "tiempo_revision": 8,
        "factor_impacto": 24.31
    },
    {
        "nombre": "Journal of Applied Physics",
        "area": "fisica",
        "indexacion": "scopus q2",
        "apc": "no",
        "tiempo_revision": 3,
        "factor_impacto": 2.87
    },
    {
        "nombre": "Revista Mexicana de Fisica",
        "area": "fisica",
        "indexacion": "scielo",
        "apc": "no",
        "tiempo_revision": 4,
        "factor_impacto": 0.65
    },
    {
        "nombre": "PLOS ONE",
        "area": "multidisciplinaria",
        "indexacion": "scopus q1",
        "apc": "si",
        "tiempo_revision": 3,
        "factor_impacto": 3.75
    },
    {
        "nombre": "Journal of Cleaner Production",
        "area": "ciencias ambientales",
        "indexacion": "scopus q1",
        "apc": "si",
        "tiempo_revision": 7,
        "factor_impacto": 11.07
    },
    {
        "nombre": "Boletin de Linguistica",
        "area": "linguistica",
        "indexacion": "scielo",
        "apc": "no",
        "tiempo_revision": 6,
        "factor_impacto": 0.25
    },
    {
        "nombre": "Investigacion Bibliotecologica",
        "area": "bibliotecologia",
        "indexacion": "latindex",
        "apc": "no",
        "tiempo_revision": 4,
        "factor_impacto": 0.45
    },
    {
        "nombre": "Revista Latinoamericana de Psicologia",
        "area": "psicologia",
        "indexacion": "latindex",
        "apc": "no",
        "tiempo_revision": 5,
        "factor_impacto": 0.82
    }
]

# ============================================================
# RELACIONES LOGICAS (kanren)
# ============================================================

if KANREN_AVAILABLE:
    indexacion_rel = Relation()
    area_rel = Relation()
    apc_rel = Relation()

    for revista in base_datos:
        facts(indexacion_rel, (revista["nombre"], revista["indexacion"]))
        facts(area_rel, (revista["nombre"], revista["area"]))
        facts(apc_rel, (revista["nombre"], revista["apc"]))


# ============================================================
# FUNCIONES DE INFERENCIA LOGICA
# ============================================================

def aplicar_reglas(preferencias):
    """Aplica reglas logicas para filtrar revistas segun preferencias.

    Utiliza kanren para inferir que revistas cumplen estrictamente
    las condiciones definidas por el usuario.

    PARADIGMA LOGICO:
    - Hechos: atributos modelados como relaciones (indexacion_rel, etc.)
    - Consultas: run() con variables logicas (var()) y goals
    - Conjuncion (AND): multiples goals en run()
    - Disyuncion (OR): conde() para alternativas
    - Inferencia: deduccion de candidatos a partir de hechos+reglas

    Args:
        preferencias: dict con claves 'area', 'indexacion', 'apc',
                      'tiempo_max', 'impacto_min'.

    Returns:
        list[dict]: revistas de base_datos que cumplen las reglas.
    """
    if not KANREN_AVAILABLE:
        return _filtrar_fallback(preferencias)

    x = var()
    idx_pref = preferencias.get("indexacion", "").strip().lower()
    area_pref = preferencias.get("area", "").strip().lower()
    apc_pref = preferencias.get("apc", "").strip().lower()

    # Construir goals base (AND logico) - excluyendo area
    goals_base = []
    if idx_pref and idx_pref not in ("cualquier", ""):
        goals_base.append(indexacion_rel(x, idx_pref))
    if apc_pref and apc_pref not in ("cualquier", ""):
        goals_base.append(apc_rel(x, apc_pref))

    # Determinar names validos segun los filtros
    if not area_pref and not goals_base:
        # Sin filtros: todas las revistas
        nombres_validos = set(j["nombre"] for j in base_datos)

    elif not area_pref and goals_base:
        # Filtros no-area solamente
        nombres_validos = set(run(0, x, *goals_base))

    elif area_pref and not goals_base:
        # Solo filtro de area, con ampliacion multidisciplinaria
        # conde expresa: area = area_pref OR area = "multidisciplinaria"
        regla_ampliacion = conde(
            [area_rel(x, area_pref)],
            [area_rel(x, "multidisciplinaria")]
        )
        nombres_validos = set(run(0, x, regla_ampliacion))

    else:
        # Area + otros filtros
        # Coincidencia estricta: area exacta + goals_base (AND)
        estrictos = set(run(0, x, area_rel(x, area_pref), *goals_base))
        # Ampliacion: (area exacta OR multidisciplinaria) + goals_base
        regla_ampliacion = conde(
            [area_rel(x, area_pref)],
            [area_rel(x, "multidisciplinaria")]
        )
        ampliados = set(run(0, x, regla_ampliacion, *goals_base))
        nombres_validos = estrictos | ampliados

    # Reconstruir lista de dicts
    resultado = [j for j in base_datos if j["nombre"] in nombres_validos]

    # Filtros numericos (fuera de kanren)
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

    return resultado


def _filtrar_fallback(preferencias):
    """Modo fallback cuando kanren no esta instalado.

    Implementa el mismo comportamiento con Python puro.
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

    return resultado


def obtener_areas_disponibles():
    """Retorna lista de areas tematicas disponibles.

    Returns:
        list[str]: areas unicas ordenadas.
    """
    return sorted(set(j["area"] for j in base_datos))


def obtener_indexaciones_disponibles():
    """Retorna lista de niveles de indexacion disponibles.

    Returns:
        list[str]: indexaciones unicas ordenadas.
    """
    return sorted(set(j["indexacion"] for j in base_datos))
