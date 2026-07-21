"""Modulo funcional: Procesamiento de datos y calculo de rankings.

Paradigma funcional:
- Funciones PURAS: sin efectos secundarios, mismo input -> mismo output.
- Uso intensivo de map(), filter(), reduce() para transformar datos.
- Lambdas para funciones anonimas de corta duracion.
- Composicion de funciones: compose() y pipe() permiten encadenar
  transformaciones de forma declarativa.
- Aplicacion parcial: functools.partial() fija argumentos, generando
  funciones especializadas a partir de funciones generales.
- Memoizacion: @lru_cache evita recalculos costosos (transparencia
  referencial => cachear es seguro).
- Inmutabilidad: no se modifican estructuras originales, se crean nuevas.
- sorted() con key=lambda para ordenamiento declarativo.
- EXTRACCION DE TERMINOS: el titulo y resumen del articulo del
  investigador se procesan para obtener terminos relevantes (limpiando
  stopwords en espanol), que alimentan el puntaje de coincidencia
  tematica. Es un pipeline funcional puro (split -> filter -> map).
"""

from functools import reduce, partial, lru_cache
from typing import Dict, List, Tuple, Optional, Callable, Any

# ============================================================
# STOPWORDS (vocabulario funcional cerrado e inmutable)
# ============================================================
# Lista de palabras vacias en espanol + Ingles tecnico basico. Se usa
# como conjunto inmutable (frozenset) para filtrar terminos irrelevantes
# al extraer las palabras del titulo y resumen del articulo. Definirla como
# constante a nivel de modulo preservar la transparencia referencial de
# las funciones puras que la consumen.

_STOPWORDS: frozenset = frozenset({
    # Articulos, pronombres y preposiciones (espanol)
    "el", "la", "los", "las", "un", "una", "unos", "unas", "lo", "al", "del",
    "de", "en", "y", "o", "u", "a", "ante", "bajo", "con", "contra", "desde",
    "durante", "entre", "hacia", "hasta", "mediante", "para", "por", "segun",
    "sin", "so", "sobre", "tras", "que", "se", "su", "sus", "es", "son", "fue",
    "fueron", "era", "han", "ha", "he", "hemos", "como", "mas", "menos", "muy",
    "tambien", "pero", "porque", "cuando", "donde", "cual", "cuales", "este",
    "esta", "estos", "estas", "ese", "esa", "esos", "esas", "aquel", "aquella",
    "esto", "eso", "aquello", "no", "si", "ya", "tal", "les", "le", "te", "me",
    "nos", "os", "mi", "tu", "yo", "el", "ella", "ellos", "ellas",
    # Conectores y vacios en Ingles (frecuentes en titulos/resumenes tecnicos)
    "the", "of", "and", "in", "to", "for", "on", "with", "at", "by", "from",
    "as", "an", "is", "are", "was", "were", "be", "been", "being", "this",
    "that", "these", "those", "it", "its", "their", "our", "we", "they",
    "a", "or", "using", "use", "used", "based", "into", "through", "can",
    "will", "shall", "may", "might", "must", "should", "would", "could",
})


# ============================================================
# COMPOSICION FUNCIONAL (Higher-Order Functions)
# ============================================================

def compose(*funcs: Callable) -> Callable:
    """Compone multiples funciones de derecha a izquierda.

    FUNCION DE ORDEN SUPERIOR.
    compose(f, g, h)(x) equivale a f(g(h(x))).
    Utiliza reduce() para encadenar las funciones.

    Args:
        *funcs: funciones a componer (se aplican de derecha a izquierda).

    Returns:
        Callable: funcion compuesta resultante.

    Ejemplo:
        >>> duplicar = lambda x: x * 2
        >>> sumar_uno = lambda x: x + 1
        >>> compose(sumar_uno, duplicar)(3)  # sumar_uno(duplicar(3)) = 7
        7
    """
    return reduce(
        lambda f, g: lambda *args, **kwargs: f(g(*args, **kwargs)),
        funcs
    )


def pipe(*funcs: Callable) -> Callable:
    """Compone multiples funciones de izquierda a derecha (pipeline).

    FUNCION DE ORDEN SUPERIOR.
    pipe(f, g, h)(x) equivale a h(g(f(x))).
    Mas intuitivo que compose() para pipelines de datos.

    Args:
        *funcs: funciones a componer (se aplican de izquierda a derecha).

    Returns:
        Callable: funcion pipeline resultante.

    Ejemplo:
        >>> pipe(str.strip, str.lower, str.split)("  HOLA MUNDO  ")
        ['hola', 'mundo']
    """
    return reduce(
        lambda f, g: lambda *args, **kwargs: g(f(*args, **kwargs)),
        funcs
    )


# ============================================================
# EXTRACCION DE TERMINOS DEL ARTICULO DEL INVESTIGADOR
# ============================================================

def _tokenizar(texto: str) -> List[str]:
    """Convierte un texto en una lista de tokens normalizados.

    FUNCION PURA.
    Pipeline funcional: lower -> split por no-palabra -> filter(no vacios).
    No usa expresiones regulares complejas: simplemente separa por espacios y
    signos de puntuacion, conservando unicamente caracteres alfanumericos y
    acentos del espanol.

    Args:
        texto: cadena de entrada (titulo o resumen del articulo).

    Returns:
        Lista de tokens en minusculas, sin elementos vacios.
    """
    if not texto:
        return []
    # Normalizar a minusculas y separar por espacios/puntuacion.
    # Se conservan letras (incluidos acentos), numeros y guiones.
    limpio = texto.lower()
    # Reemplazar cualquier caracter que no sea letra, numero o guion por espacio
    import re
    tokens = re.split(r"[^a-z0-9áéíóúñü-]+", limpio)
    return list(filter(None, tokens))


def _extraer_terminos(texto: str) -> List[str]:
    """Extrae terminos relevantes de un texto eliminando stopwords.

    FUNCION PURA.
    Pipeline funcional completo:
        tokenizar -> filter(stopword) -> filter(cortas) -> unique
    Usa map()/filter() para transformar la lista de tokens en una lista
    limpia de terminos significativos. Deduplica preservando el orden de
    aparicion (orden de relevancia en el texto original).

    Args:
        texto: titulo o resumen del articulo del investigador.

    Returns:
        Lista de terminos relevantes unicos, en orden de aparicion.

    Ejemplo:
        >>> _extraer_terminos("Un sistema de recomendacion de revistas")
        ['sistema', 'recomendacion', 'revistas']
    """
    tokens = _tokenizar(texto)

    # filter: descartar stopwords y tokens demasiado cortos (<=2 caracteres),
    # que casi nunca aportan valor tematico (ej: "de", "el", "en").
    filtrados = filter(
        lambda t: len(t) > 2 and t not in _STOPWORDS,
        tokens,
    )

    # Deduplicar preservando el orden (primera aparicion = mas relevante).
    # Se implementa de forma declarativa con reduce + acumulador de vistos.
    vistos: set = set()
    unicos = reduce(
        lambda acc, t: acc + [t] if t not in vistos and not vistos.add(t) else acc,
        filtrados,
        [],
    )
    return unicos


def extraer_terminos_articulo(titulo: str, resumen: str) -> List[str]:
    """Extrae terminos relevantes combinando titulo y resumen del articulo.

    FUNCION PURA.
    Los terminos del TITULO aparecen primero (mayor peso posicional porque
    en el ranking se conservan por orden de aparicion), seguidos de los
    terminos del RESUMEN que no estuvieran ya en el titulo.

    Args:
        titulo: titulo del articulo del investigador.
        resumen: resumen (abstract) del articulo.

    Returns:
        Lista combinada de terminos relevantes (titulo + resumen), unicos.
    """
    terminos_titulo = _extraer_terminos(titulo)
    terminos_resumen = _extraer_terminos(resumen)
    # Concatenar; los duplicados ya se eliminan dentro de _extraer_terminos,
    # pero al fusionar dos textos puede haber repeticiones entre ambos.
    combinados = terminos_titulo + [
        t for t in terminos_resumen if t not in terminos_titulo
    ]
    return combinados


# ============================================================
# FUNCIONES PURAS DE PUNTAJE
# ============================================================

def puntaje_keywords(journal: Dict[str, Any], keywords: List[str]) -> float:
    """Calcula proporcion de keywords que coinciden con la revista.

    FUNCION PURA: solo depende de sus argumentos, sin efectos laterales.
    map(): aplica la lambda a cada keyword para verificar coincidencia.
    reduce(): suma los resultados parciales (coincidencias = 1, no = 0).

    Args:
        journal: datos de la revista (nombre, area).
        keywords: lista de palabras clave normalizadas.

    Returns:
        Proporcion de coincidencia en [0.0, 1.0].
    """
    if not keywords:
        return 0.0

    texto_articulo = f"{journal['nombre']} {journal['area']}".lower()

    # map + lambda: transforma cada keyword en 1.0 (coincide) o 0.0 (no)
    coincidencias = list(
        map(lambda kw: 1.0 if kw.lower() in texto_articulo else 0.0, keywords)
    )

    # reduce: acumula la suma de coincidencias
    total_coincidencias = reduce(lambda a, b: a + b, coincidencias, 0.0)
    return total_coincidencias / len(keywords)


def puntaje_tiempo(tiempo_revision: int, tiempo_max: Optional[int]) -> float:
    """Evalua que tan rapida es la revista respecto al maximo aceptable.

    FUNCION PURA.
    A menor tiempo de revision, mayor puntaje.
    Si no hay tiempo maximo definido, retorna puntaje neutral (0.5).

    Args:
        tiempo_revision: meses promedio de revision.
        tiempo_max: maximo de meses aceptable.

    Returns:
        Puntaje en [0.0, 1.0].
    """
    if not tiempo_max or tiempo_max <= 0:
        return 0.5

    puntaje = 1.0 - (tiempo_revision / (tiempo_max * 2))
    return max(0.0, puntaje)


def puntaje_impacto(factor_impacto: float, impacto_min: Optional[float]) -> float:
    """Evalua el factor de impacto contra el minimo deseado.

    FUNCION PURA.
    Normaliza el factor de impacto a [0.0, 1.0].
    Si supera el minimo, el puntaje crece proporcionalmente.

    Args:
        factor_impacto: factor de impacto de la revista.
        impacto_min: factor minimo aceptable.

    Returns:
        Puntaje en [0.0, 1.0].
    """
    if not impacto_min or impacto_min <= 0:
        return min(1.0, factor_impacto / 10.0)

    if factor_impacto < impacto_min:
        return 0.0

    return min(1.0, factor_impacto / max(impacto_min * 2, 0.01))


# ============================================================
# MEMOIZACION (evita recalculos por transparencia referencial)
# ============================================================

@lru_cache(maxsize=256)
def _puntaje_impacto_cached(
    factor_impacto: float, impacto_min: Optional[float]
) -> float:
    """Version memoizada de puntaje_impacto.

    Utiliza @lru_cache para evitar recalculos cuando se consultan
    las mismas revistas con los mismos criterios repetidamente.
    Esto es seguro porque puntaje_impacto es PURA (transparencia
    referencial: mismo input => mismo output siempre).

    Args:
        factor_impacto: factor de impacto de la revista.
        impacto_min: factor minimo aceptable.

    Returns:
        Puntaje en [0.0, 1.0].
    """
    return puntaje_impacto(factor_impacto, impacto_min)


@lru_cache(maxsize=256)
def _puntaje_tiempo_cached(
    tiempo_revision: int, tiempo_max: Optional[int]
) -> float:
    """Version memoizada de puntaje_tiempo.

    Misma logica que puntaje_tiempo, pero con cache automatico.

    Args:
        tiempo_revision: meses promedio de revision.
        tiempo_max: maximo de meses aceptable.

    Returns:
        Puntaje en [0.0, 1.0].
    """
    return puntaje_tiempo(tiempo_revision, tiempo_max)


# ============================================================
# APLICACION PARCIAL (Currying)
# ============================================================

def crear_evaluador_keywords(keywords: List[str]) -> Callable[[Dict], float]:
    """Crea una funcion evaluadora parcialmente aplicada para keywords.

    Utiliza functools.partial para fijar el argumento 'keywords',
    retornando una funcion que solo necesita el journal.
    Demuestra aplicacion parcial / currying como tecnica funcional.

    Args:
        keywords: lista de palabras clave a fijar.

    Returns:
        Funcion que recibe un journal dict y retorna su puntaje.
    """
    return partial(puntaje_keywords, keywords=keywords)


# ============================================================
# CALCULO DE PUNTAJE TOTAL (COMPOSICION FUNCIONAL)
# ============================================================

def _calcular_puntajes_parciales(
    journal: Dict[str, Any],
    keywords: List[str],
    tiempo_max: Optional[int],
    impacto_min: Optional[float],
) -> Dict[str, float]:
    """Calcula todos los puntajes parciales para una revista.

    FUNCION PURA auxiliar.
    Usa versiones memoizadas de las funciones de tiempo e impacto
    para evitar recalculos en consultas repetidas.

    Args:
        journal: datos de la revista.
        keywords: palabras clave normalizadas.
        tiempo_max: tiempo maximo aceptable.
        impacto_min: impacto minimo aceptable.

    Returns:
        Dict con puntajes parciales: 'keywords', 'tiempo', 'impacto'.
    """
    return {
        "keywords": puntaje_keywords(journal, keywords),
        "tiempo": _puntaje_tiempo_cached(journal["tiempo_revision"], tiempo_max),
        "impacto": _puntaje_impacto_cached(journal["factor_impacto"], impacto_min),
    }


def calcular_puntaje_total(
    journal: Dict[str, Any],
    keywords: List[str],
    tiempo_max: Optional[int],
    impacto_min: Optional[float],
) -> Tuple[float, Dict[str, float]]:
    """Calcula el puntaje total ponderado de una revista.

    FUNCION PURA.
    reduce(): acumula los puntajes parciales multiplicados por sus pesos.
    Los pesos son: keywords 40%, tiempo 30%, impacto 30%.

    Args:
        journal: datos de la revista.
        keywords: palabras clave normalizadas.
        tiempo_max: tiempo maximo de revision.
        impacto_min: factor de impacto minimo.

    Returns:
        Tupla (puntaje_total_redondeado, dict_puntajes_parciales).
    """
    pesos: Dict[str, float] = {"keywords": 0.4, "tiempo": 0.3, "impacto": 0.3}
    parciales = _calcular_puntajes_parciales(journal, keywords, tiempo_max, impacto_min)

    # reduce: acumula la suma ponderada sobre las claves de pesos
    total = reduce(lambda acc, k: acc + parciales[k] * pesos[k], pesos.keys(), 0.0)
    return round(total, 4), parciales


# ============================================================
# FUNCIONES AUXILIARES PURAS
# ============================================================

def _parsear_keywords(palabras_raw: str) -> List[str]:
    """Extrae y limpia keywords de una cadena separada por comas.

    FUNCION PURA.
    Pipeline funcional: split -> map(strip) -> filter(no vacias).

    Args:
        palabras_raw: cadena con keywords separadas por coma.

    Returns:
        Lista de keywords limpias (sin elementos vacios).
    """
    return list(
        filter(None, map(lambda s: s.strip(), palabras_raw.split(",")))
    )


def _parsear_numero(valor: str, tipo: type = float) -> Optional[float]:
    """Parsea un valor numerico de forma segura.

    FUNCION PURA: retorna None en lugar de lanzar excepciones.

    Args:
        valor: string a parsear.
        tipo: tipo numerico destino (int o float).

    Returns:
        Valor numerico parseado, o None si no es parseable.
    """
    try:
        return tipo(valor) if valor else None
    except (ValueError, TypeError):
        return None


def _enriquecer_revista(
    journal: Dict[str, Any],
    keywords: List[str],
    tiempo_max: Optional[int],
    impacto_min: Optional[float],
) -> Dict[str, Any]:
    """Enriquece una revista con sus puntajes calculados.

    FUNCION PURA.
    Crea un NUEVO dict (inmutabilidad) sin modificar el original.
    Resuelve el bug de doble computo: calcular_puntaje_total()
    se invoca UNA sola vez y se desestructura en (total, parciales).

    Args:
        journal: datos originales de la revista.
        keywords: palabras clave normalizadas.
        tiempo_max: tiempo maximo aceptable.
        impacto_min: impacto minimo aceptable.

    Returns:
        Nuevo dict con campos puntaje_total y puntajes_parciales agregados.
    """
    total, parciales = calcular_puntaje_total(journal, keywords, tiempo_max, impacto_min)
    return {**journal, "puntaje_total": total, "puntajes_parciales": parciales}


# ============================================================
# FUNCION PRINCIPAL DE RANKING (PIPELINE FUNCIONAL)
# ============================================================

def rankear_revistas(
    revistas: List[Dict[str, Any]],
    preferencias: Dict[str, str],
) -> List[Dict[str, Any]]:
    """Rankea las revistas candidatas usando procesamiento funcional puro.

    FUNCION PURA.
    Pipeline funcional completo:
    1. _parsear_keywords(): extrae keywords con map() + filter().
    2. partial(): crea evaluador parcialmente aplicado.
    3. compose(): construye pipeline declarativo de transformaciones.
    4. map(): transforma cada revista en un dict enriquecido.
    5. sorted() con key=lambda: ordena descendente por puntaje_total.

    Args:
        revistas: lista de revistas pre-filtradas por logic_rules.
        preferencias: preferencias del usuario con claves
                    'palabras_clave', 'tiempo_max', 'impacto_min'.

    Returns:
        Revistas ordenadas por puntaje_total descendente, cada una
        enriquecida con 'puntaje_total' y 'puntajes_parciales'.
    """
    # Paso 1: parsear keywords con pipeline funcional (map + filter)
    keywords = _parsear_keywords(preferencias.get("palabras_clave", ""))

    # Paso 1b: extraer terminos relevantes del titulo + resumen del
    # articulo del investigador (pipeline funcional tokenizar+filter).
    # Estos terminos se fusionan con las keywords manuales: asi el
    # puntaje de coincidencia tematica aprovecha TODO el contenido del
    # articulo, no solo las palabras clave que el usuario escribio a mano.
    terminos_articulo = extraer_terminos_articulo(
        preferencias.get("titulo", ""),
        preferencias.get("resumen", ""),
    )

    # Fusionar sin duplicados: keywords manuales primero (peso posicional),
    # luego terminos extraidos del titulo/resumen que no estuvieran ya.
    keywords_combinadas = keywords + [
        t for t in terminos_articulo if t not in keywords
    ]

    # Paso 2: parsear parametros numericos con funciones puras
    tiempo_max = _parsear_numero(preferencias.get("tiempo_max", ""), int)
    impacto_min = _parsear_numero(preferencias.get("impacto_min", ""), float)

    # Paso 3: crear evaluador parcialmente aplicado (partial / currying)
    # Fija keywords_combinadas, tiempo_max e impacto_min; la funcion
    # resultante solo necesita recibir el journal.
    enriquecer = partial(
        _enriquecer_revista,
        keywords=keywords_combinadas,
        tiempo_max=tiempo_max,
        impacto_min=impacto_min,
    )

    # Paso 4: construir pipeline funcional con compose()
    # Lee de derecha a izquierda:
    #   1. map(enriquecer) => agrega puntajes a cada revista
    #   2. list()          => materializa el iterador
    #   3. sorted(...)     => ordena por puntaje descendente
    pipeline_ranking = compose(
        partial(sorted, key=lambda r: r["puntaje_total"], reverse=True),
        list,
        partial(map, enriquecer),
    )

    return pipeline_ranking(revistas)
