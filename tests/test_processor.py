"""Tests para el modulo funcional (processor.py).

Verifica las funciones puras de puntaje, la composicion funcional,
la memoizacion y el pipeline de ranking.
"""

import pytest
from processor import (
    puntaje_keywords,
    puntaje_tiempo,
    puntaje_impacto,
    calcular_puntaje_total,
    rankear_revistas,
    compose,
    pipe,
    crear_evaluador_keywords,
    _parsear_keywords,
    _parsear_numero,
    _enriquecer_revista,
)


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture
def revista_nature():
    """Fixture: datos de Nature para pruebas."""
    return {
        "nombre": "Nature",
        "area": "multidisciplinaria",
        "indexacion": "scopus q1",
        "apc": "si",
        "tiempo_revision": 6,
        "factor_impacto": 49.96,
    }


@pytest.fixture
def revista_plos():
    """Fixture: datos de PLOS ONE para pruebas."""
    return {
        "nombre": "PLOS ONE",
        "area": "multidisciplinaria",
        "indexacion": "scopus q1",
        "apc": "si",
        "tiempo_revision": 3,
        "factor_impacto": 3.75,
    }


@pytest.fixture
def lista_revistas(revista_nature, revista_plos):
    """Fixture: lista de revistas para ranking."""
    return [revista_nature, revista_plos]


# ============================================================
# TESTS: puntaje_keywords (funcion pura)
# ============================================================

class TestPuntajeKeywords:
    """Tests para la funcion pura puntaje_keywords."""

    def test_coincidencia_total(self, revista_nature):
        """Keywords que coinciden completamente."""
        assert puntaje_keywords(revista_nature, ["nature"]) == 1.0

    def test_sin_coincidencia(self, revista_nature):
        """Keywords que no coinciden."""
        assert puntaje_keywords(revista_nature, ["robotica"]) == 0.0

    def test_coincidencia_parcial(self, revista_nature):
        """Mezcla de keywords que coinciden y no."""
        result = puntaje_keywords(revista_nature, ["nature", "robotica"])
        assert result == 0.5

    def test_keywords_vacias(self, revista_nature):
        """Lista vacia de keywords retorna 0.0."""
        assert puntaje_keywords(revista_nature, []) == 0.0

    def test_coincidencia_por_area(self, revista_nature):
        """Keywords que coinciden con el area de la revista."""
        result = puntaje_keywords(revista_nature, ["multidisciplinaria"])
        assert result == 1.0

    def test_case_insensitive(self, revista_nature):
        """La busqueda no es sensible a mayusculas."""
        assert puntaje_keywords(revista_nature, ["NATURE"]) == 1.0

    def test_es_funcion_pura(self, revista_nature):
        """Verificar que es funcion pura: mismo input, mismo output."""
        kw = ["nature", "ciencia"]
        r1 = puntaje_keywords(revista_nature, kw)
        r2 = puntaje_keywords(revista_nature, kw)
        assert r1 == r2


# ============================================================
# TESTS: puntaje_tiempo (funcion pura)
# ============================================================

class TestPuntajeTiempo:
    """Tests para la funcion pura puntaje_tiempo."""

    def test_tiempo_rapido(self):
        """Revista rapida (3 meses) con maximo 12."""
        result = puntaje_tiempo(3, 12)
        assert result > 0.8

    def test_tiempo_igual_maximo(self):
        """Revista con tiempo = maximo / 2."""
        result = puntaje_tiempo(6, 6)
        assert result == 0.5

    def test_sin_tiempo_max(self):
        """Sin tiempo maximo retorna 0.5 (neutral)."""
        assert puntaje_tiempo(6, None) == 0.5

    def test_tiempo_max_cero(self):
        """Tiempo maximo 0 retorna neutral."""
        assert puntaje_tiempo(6, 0) == 0.5

    def test_resultado_no_negativo(self):
        """El puntaje nunca es negativo."""
        result = puntaje_tiempo(100, 1)
        assert result >= 0.0


# ============================================================
# TESTS: puntaje_impacto (funcion pura)
# ============================================================

class TestPuntajeImpacto:
    """Tests para la funcion pura puntaje_impacto."""

    def test_alto_impacto_sin_minimo(self):
        """Alto impacto sin minimo definido."""
        result = puntaje_impacto(49.96, None)
        assert result == 1.0  # min(1.0, 49.96/10) = 1.0

    def test_impacto_supera_minimo(self):
        """Impacto que supera el minimo."""
        result = puntaje_impacto(5.0, 2.0)
        assert result > 0.0
        assert result <= 1.0

    def test_impacto_menor_que_minimo(self):
        """Impacto menor al minimo retorna 0."""
        result = puntaje_impacto(1.0, 5.0)
        assert result == 0.0

    def test_impacto_minimo_cero(self):
        """Minimo 0 usa la normalizacion por defecto."""
        result = puntaje_impacto(5.0, 0)
        assert result == 0.5  # min(1.0, 5.0/10.0) = 0.5

    def test_resultado_acotado(self):
        """El puntaje esta entre 0.0 y 1.0."""
        result = puntaje_impacto(100.0, 1.0)
        assert 0.0 <= result <= 1.0


# ============================================================
# TESTS: calcular_puntaje_total
# ============================================================

class TestCalcularPuntajeTotal:
    """Tests para la funcion de puntaje total ponderado."""

    def test_retorna_tupla(self, revista_nature):
        """Retorna tupla (total, parciales)."""
        total, parciales = calcular_puntaje_total(
            revista_nature, ["nature"], 12, 1.0
        )
        assert isinstance(total, float)
        assert isinstance(parciales, dict)

    def test_parciales_tienen_tres_claves(self, revista_nature):
        """Los parciales contienen keywords, tiempo, impacto."""
        _, parciales = calcular_puntaje_total(
            revista_nature, ["nature"], 12, 1.0
        )
        assert "keywords" in parciales
        assert "tiempo" in parciales
        assert "impacto" in parciales

    def test_total_es_ponderacion(self, revista_nature):
        """El total es la suma ponderada de los parciales."""
        total, parciales = calcular_puntaje_total(
            revista_nature, ["nature"], 12, 1.0
        )
        esperado = (
            parciales["keywords"] * 0.4
            + parciales["tiempo"] * 0.3
            + parciales["impacto"] * 0.3
        )
        assert abs(total - round(esperado, 4)) < 0.001

    def test_total_acotado(self, revista_nature):
        """El puntaje total esta entre 0.0 y 1.0."""
        total, _ = calcular_puntaje_total(
            revista_nature, ["nature"], 12, 1.0
        )
        assert 0.0 <= total <= 1.0


# ============================================================
# TESTS: compose y pipe (composicion funcional)
# ============================================================

class TestComposicionFuncional:
    """Tests para las funciones de composicion."""

    def test_compose_dos_funciones(self):
        """compose(f, g)(x) = f(g(x))."""
        duplicar = lambda x: x * 2
        sumar_uno = lambda x: x + 1
        f = compose(sumar_uno, duplicar)
        assert f(3) == 7  # sumar_uno(duplicar(3)) = 7

    def test_pipe_dos_funciones(self):
        """pipe(f, g)(x) = g(f(x))."""
        duplicar = lambda x: x * 2
        sumar_uno = lambda x: x + 1
        f = pipe(duplicar, sumar_uno)
        assert f(3) == 7  # sumar_uno(duplicar(3)) = 7

    def test_compose_identidad(self):
        """compose con funcion identidad."""
        identidad = lambda x: x
        duplicar = lambda x: x * 2
        f = compose(identidad, duplicar)
        assert f(5) == 10

    def test_pipe_tres_funciones(self):
        """pipe con tres funciones encadenadas."""
        f = pipe(
            lambda x: x + 1,
            lambda x: x * 2,
            lambda x: x - 3,
        )
        assert f(5) == 9  # ((5+1)*2) - 3 = 9


# ============================================================
# TESTS: aplicacion parcial
# ============================================================

class TestAplicacionParcial:
    """Tests para crear_evaluador_keywords (partial)."""

    def test_evaluador_parcial(self, revista_nature):
        """crear_evaluador_keywords crea funcion parcialmente aplicada."""
        evaluar = crear_evaluador_keywords(["nature"])
        result = evaluar(revista_nature)
        assert result == 1.0

    def test_evaluador_sin_coincidencia(self, revista_nature):
        """Evaluador parcial con keywords que no coinciden."""
        evaluar = crear_evaluador_keywords(["quimica"])
        result = evaluar(revista_nature)
        assert result == 0.0


# ============================================================
# TESTS: parseo de datos
# ============================================================

class TestParseo:
    """Tests para funciones de parseo."""

    def test_parsear_keywords_normales(self):
        """Parsea keywords separadas por coma."""
        result = _parsear_keywords("machine learning, deep learning, AI")
        assert len(result) == 3
        assert "machine learning" in result

    def test_parsear_keywords_con_vacias(self):
        """Elimina keywords vacias."""
        result = _parsear_keywords("a, , b, ,c")
        assert len(result) == 3

    def test_parsear_keywords_cadena_vacia(self):
        """Cadena vacia retorna lista con string vacio filtrado."""
        result = _parsear_keywords("")
        assert result == []

    def test_parsear_numero_valido(self):
        """Parsea numero float valido."""
        assert _parsear_numero("3.5", float) == 3.5

    def test_parsear_numero_invalido(self):
        """Numero invalido retorna None."""
        assert _parsear_numero("abc", float) is None

    def test_parsear_numero_vacio(self):
        """Cadena vacia retorna None."""
        assert _parsear_numero("", int) is None


# ============================================================
# TESTS: rankear_revistas (pipeline completo)
# ============================================================

class TestRankearRevistas:
    """Tests para el pipeline funcional completo."""

    def test_retorna_lista_ordenada(self, lista_revistas):
        """El resultado esta ordenado por puntaje descendente."""
        prefs = {"palabras_clave": "nature", "tiempo_max": "12", "impacto_min": "1"}
        result = rankear_revistas(lista_revistas, prefs)
        assert len(result) == 2
        assert result[0]["puntaje_total"] >= result[1]["puntaje_total"]

    def test_contiene_puntaje_total(self, lista_revistas):
        """Cada resultado tiene puntaje_total."""
        prefs = {"palabras_clave": "", "tiempo_max": "", "impacto_min": ""}
        result = rankear_revistas(lista_revistas, prefs)
        for r in result:
            assert "puntaje_total" in r
            assert "puntajes_parciales" in r

    def test_lista_vacia(self):
        """Rankear lista vacia retorna lista vacia."""
        prefs = {"palabras_clave": "", "tiempo_max": "", "impacto_min": ""}
        result = rankear_revistas([], prefs)
        assert result == []

    def test_preserva_datos_originales(self, lista_revistas):
        """El ranking preserva los datos originales de cada revista."""
        prefs = {"palabras_clave": "nature", "tiempo_max": "", "impacto_min": ""}
        result = rankear_revistas(lista_revistas, prefs)
        nombres = [r["nombre"] for r in result]
        assert "Nature" in nombres
        assert "PLOS ONE" in nombres

    def test_inmutabilidad(self, lista_revistas):
        """rankear_revistas no modifica la lista original."""
        prefs = {"palabras_clave": "nature", "tiempo_max": "", "impacto_min": ""}
        original_len = len(lista_revistas)
        rankear_revistas(lista_revistas, prefs)
        assert len(lista_revistas) == original_len
        assert "puntaje_total" not in lista_revistas[0]
