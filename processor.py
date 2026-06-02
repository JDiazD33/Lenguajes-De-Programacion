"""Modulo funcional: Procesamiento de datos y calculo de rankings.

Paradigma funcional:
- Funciones PURAS: sin efectos secundarios, mismo input -> mismo output.
- Uso intensivo de map(), filter(), reduce() para transformar datos.
- Lambdas para funciones anonimas de corta duracion.
- Composicion de funciones: el output de una es input de otra.
- Inmutabilidad: no se modifican estructuras originales, se crean nuevas.
- sorted() con key=lambda para ordenamiento declarativo.
"""

from functools import reduce


# ============================================================
# FUNCIONES PURAS DE PUNTAJE
# ============================================================

def puntaje_keywords(journal, keywords):
    """Calcula proporcion de keywords que coinciden con la revista.

    FUNCION PURA: solo depende de sus argumentos, sin efectos laterales.
    map(): aplica la lambda a cada keyword para verificar coincidencia.
    reduce(): suma los resultados parciales (coincidencias = 1, no = 0).

    Args:
        journal (dict): datos de la revista (nombre, area).
        keywords (list[str]): lista de palabras clave normalizadas.

    Returns:
        float: proporcion de coincidencia en [0.0, 1.0].
    """
    if not keywords:
        return 0.0

    texto_articulo = f"{journal['nombre']} {journal['area']}".lower()

    coincidencias = list(
        map(lambda kw: 1.0 if kw.lower() in texto_articulo else 0.0, keywords)
    )

    total_coincidencias = reduce(lambda a, b: a + b, coincidencias, 0.0)
    return total_coincidencias / len(keywords)


def puntaje_tiempo(tiempo_revision, tiempo_max):
    """Evalua que tan rapida es la revista respecto al maximo aceptable.

    FUNCION PURA.
    A menor tiempo de revision, mayor puntaje.
    Si no hay tiempo maximo definido, retorna puntaje neutral (0.5).

    Args:
        tiempo_revision (int): meses promedio de revision.
        tiempo_max (int|None): maximo de meses aceptable.

    Returns:
        float: puntaje en [0.0, 1.0].
    """
    if not tiempo_max or tiempo_max <= 0:
        return 0.5

    puntaje = 1.0 - (tiempo_revision / (tiempo_max * 2))
    return max(0.0, puntaje)


def puntaje_impacto(factor_impacto, impacto_min):
    """Evalua el factor de impacto contra el minimo deseado.

    FUNCION PURA.
    Normaliza el factor de impacto a [0.0, 1.0].
    Si supera el minimo, el puntaje crece proporcionalmente.

    Args:
        factor_impacto (float): factor de impacto de la revista.
        impacto_min (float|None): factor minimo aceptable.

    Returns:
        float: puntaje en [0.0, 1.0].
    """
    if not impacto_min or impacto_min <= 0:
        return min(1.0, factor_impacto / 10.0)

    if factor_impacto < impacto_min:
        return 0.0

    return min(1.0, factor_impacto / max(impacto_min * 2, 0.01))


def _calcular_puntajes_parciales(journal, keywords, tiempo_max, impacto_min):
    """Calcula todos los puntajes parciales para una revista.

    FUNCION PURA auxiliar.
    Retorna un dict con cada dimension de puntaje.

    Args:
        journal (dict): datos de la revista.
        keywords (list[str]): palabras clave normalizadas.
        tiempo_max (int|None): tiempo maximo aceptable.
        impacto_min (float|None): impacto minimo aceptable.

    Returns:
        dict: puntajes parciales con claves 'keywords', 'tiempo', 'impacto'.
    """
    return {
        "keywords": puntaje_keywords(journal, keywords),
        "tiempo": puntaje_tiempo(journal["tiempo_revision"], tiempo_max),
        "impacto": puntaje_impacto(journal["factor_impacto"], impacto_min),
    }


def calcular_puntaje_total(journal, keywords, tiempo_max, impacto_min):
    """Calcula el puntaje total ponderado de una revista.

    FUNCION PURA.
    reduce(): acumula los puntajes parciales multiplicados por sus pesos.
    Los pesos son: keywords 40%, tiempo 30%, impacto 30%.

    Args:
        journal (dict): datos de la revista.
        keywords (list[str]): palabras clave normalizadas.
        tiempo_max (int|None): tiempo maximo de revision.
        impacto_min (float|None): factor de impacto minimo.

    Returns:
        tuple[float, dict]: (puntaje_total_redondeado, puntajes_parciales).
    """
    pesos = {"keywords": 0.4, "tiempo": 0.3, "impacto": 0.3}
    parciales = _calcular_puntajes_parciales(journal, keywords, tiempo_max, impacto_min)

    total = reduce(lambda acc, k: acc + parciales[k] * pesos[k], pesos.keys(), 0.0)
    return round(total, 4), parciales


# ============================================================
# FUNCION PRINCIPAL DE RANKING (ESTILO FUNCIONAL)
# ============================================================

def rankear_revistas(revistas, preferencias):
    """Rankea las revistas candidatas usando procesamiento funcional.

    FUNCION PURA.
    Flujo funcional:
    1. filter(): elimina cadenas vacias de las keywords.
    2. map(): transforma cada revista en un dict enriquecido con
       puntaje_total y puntajes_parciales.
    3. sorted() con key=lambda: ordena descendente por puntaje_total.

    Args:
        revistas (list[dict]): lista de revistas a rankear (pre-filtradas
                               por logic_rules).
        preferencias (dict): preferencias del usuario incluyendo
                            'palabras_clave', 'tiempo_max', 'impacto_min'.

    Returns:
        list[dict]: revistas ordenadas por puntaje_total descendente,
                    cada una con sus puntajes anidados.
    """
    palabras_raw = preferencias.get("palabras_clave", "")

    # filter(): elimina keywords vacias o solo-espacios
    keywords = list(
        filter(None, map(lambda s: s.strip(), palabras_raw.split(",")))
    )

    tiempo_max = None
    impacto_min = None
    try:
        if preferencias.get("tiempo_max"):
            tiempo_max = int(preferencias["tiempo_max"])
        if preferencias.get("impacto_min"):
            impacto_min = float(preferencias["impacto_min"])
    except (ValueError, TypeError):
        pass

    # map(): enriquece cada revista con puntajes
    # reduce() dentro de calcular_puntaje_total para ponderacion
    # lambda para construir el nuevo dict
    resultados = list(
        map(
            lambda j: {
                **j,
                "puntaje_total": calcular_puntaje_total(
                    j, keywords, tiempo_max, impacto_min
                )[0],
                "puntajes_parciales": calcular_puntaje_total(
                    j, keywords, tiempo_max, impacto_min
                )[1],
            },
            revistas,
        )
    )

    # sorted() con key=lambda: ordenamiento funcional descendente
    return sorted(resultados, key=lambda r: r["puntaje_total"], reverse=True)
