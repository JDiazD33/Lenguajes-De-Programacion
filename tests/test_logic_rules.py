"""Tests para el modulo logico (logic_rules.py).

Verifica hechos base, relaciones derivadas, reglas compuestas y consultas logicas con kanren.

"""

import pytest
from logic_rules import (
    KANREN_AVAILABLE,
    base_datos,
    consultar_destacadas,
    consultar_accesibles,
    consultar_emergentes,
    _obtener_etiquetas_logicas,
    aplicar_reglas,
    obtener_areas_disponibles,
    obtener_indexaciones_disponibles,
    _filtrar_fallback,
)

if KANREN_AVAILABLE:
    from kanren import var, run
    from logic_rules import (
        indexacion_rel,
        area_rel,
        apc_rel,
        alto_impacto,
        medio_impacto,
        bajo_impacto,
        publicacion_rapida,
        publicacion_moderada,
        publicacion_lenta,
        acceso_abierto,
        acceso_pago,
        regla_revista_destacada,
        regla_revista_accesible,
        regla_revista_emergente,
    )


# ============================================================
# TESTS: Base de Datos y Estructura
# ============================================================

def test_base_datos_consistencia():
    """Verifica que la base de datos contenga al menos 10 revistas con estructura correcta."""
    assert len(base_datos) >= 10
    for j in base_datos:
        assert "nombre" in j
        assert "area" in j
        assert "indexacion" in j
        assert "apc" in j
        assert "tiempo_revision" in j
        assert "factor_impacto" in j
        assert isinstance(j["nombre"], str)
        assert isinstance(j["area"], str)
        assert isinstance(j["indexacion"], str)
        assert j["apc"] in ("si", "no")
        assert isinstance(j["tiempo_revision"], int)
        assert isinstance(j["factor_impacto"], (int, float))


# ============================================================
# TESTS: Relaciones y Reglas Logicas (Kanren)
# ============================================================

@pytest.mark.skipif(not KANREN_AVAILABLE, reason="Kanren no esta instalado en el sistema")
class TestReglasKanren:
    """Pruebas especificas para la unificacion y reglas de Kanren."""

    def test_relaciones_base(self):
        """Verifica que los hechos de relaciones base esten bien cargados."""
        x = var()
        # Verificar area de Nature
        areas_nature = list(run(0, x, area_rel("Nature", x)))
        assert "multidisciplinaria" in areas_nature

        # Verificar apc de Nature
        apc_nature = list(run(0, x, apc_rel("Nature", x)))
        assert "si" in apc_nature

        # Verificar indexacion de Nature
        idx_nature = list(run(0, x, indexacion_rel("Nature", x)))
        assert "scopus q1" in idx_nature

    def test_relaciones_derivadas(self):
        """Verifica que las relaciones numericas derivadas esten bien pobladas."""
        x = var()
        
        # Nature (FI = 49.96) debe ser de alto impacto
        revistas_alto_impacto = list(run(0, x, alto_impacto(x)))
        assert "Nature" in revistas_alto_impacto
        assert "Science" in revistas_alto_impacto
        
        # Revista Mexicana de Fisica (FI = 0.65) debe ser de bajo impacto
        revistas_bajo_impacto = list(run(0, x, bajo_impacto(x)))
        assert "Revista Mexicana de Fisica" in revistas_bajo_impacto
        
        # Journal of Applied Physics (tiempo = 3) debe ser de publicacion rapida
        revistas_rapidas = list(run(0, x, publicacion_rapida(x)))
        assert "Journal of Applied Physics" in revistas_rapidas

    def test_reglas_compuestas(self):
        """Verifica la ejecucion directa de reglas compuestas."""
        x = var()
        
        # Revista destacada: alto impacto y revision rapida/moderada (Nature: FI=49.96, tiempo=6)
        destacadas = list(run(0, x, regla_revista_destacada(x)))
        assert "Nature" in destacadas
        assert "Science" in destacadas
        
        # Revista accesible: abierta y al menos impacto medio/alto
        accesibles = list(run(0, x, regla_revista_accesible(x)))
        # PLOS ONE es abierta y FI = 3.75 (medio) -> accesible (aunque cobra APC = si, pero en base_datos apc es "si",
        # wait, PLOS ONE apc es "si" en base_datos, y en la regla dice accesible si es acceso_abierto (apc == "no")
        # Veamos que revistas en base_datos tienen apc=="no" y FI >= 1.0: Journal of Applied Physics (apc="no", FI=2.87)
        assert "Journal of Applied Physics" in accesibles
        
        # Revista emergente: abierta, bajo impacto y rapida.
        # Revista Mexicana de Fisica (apc="no", FI=0.65, tiempo=4) -> emergente
        emergentes = list(run(0, x, regla_revista_emergente(x)))
        assert "Revista Mexicana de Fisica" in emergentes


# ============================================================
# TESTS: Consultas Publicas (Compatibles con y sin Kanren)
# ============================================================

class TestConsultasLogicas:
    """Verifica las funciones de consulta logica del modulo."""

    def test_consultar_destacadas(self):
        """Valida que consultar_destacadas devuelva revistas con FI >= 10 y tiempo <= 6."""
        res = consultar_destacadas()
        assert isinstance(res, list)
        assert "Nature" in res
        assert "Science" in res
        assert "Journal of Cleaner Production" not in res  # tiempo = 7 (>6)

    def test_consultar_accesibles(self):
        """Valida que consultar_accesibles devuelva revistas abiertas con FI >= 1.0."""
        res = consultar_accesibles()
        assert isinstance(res, list)
        assert "Journal of Applied Physics" in res
        assert "Nature" not in res  # apc = si

    def test_consultar_emergentes(self):
        """Valida que consultar_emergentes devuelva revistas abiertas, rapidas y con FI < 1.0."""
        res = consultar_emergentes()
        assert isinstance(res, list)
        assert "Revista Mexicana de Fisica" in res
        assert "Nature" not in res  # apc = si, FI = 49.96


# ============================================================
# TESTS: Obtener Etiquetas Logicas
# ============================================================

class TestEtiquetadoLogico:
    """Verifica la asignacion de etiquetas inferidas semanticas."""

    def test_etiquetado_nature(self):
        """Nature debe ser catalogada como Destacada y Alto Impacto."""
        etiquetas = _obtener_etiquetas_logicas("Nature")
        assert "Destacada" in etiquetas
        assert "Alto Impacto" in etiquetas
        assert "Emergente" not in etiquetas

    def test_etiquetado_mexicana_fisica(self):
        """Revista Mexicana de Fisica debe ser emergente e impacto bajo."""
        etiquetas = _obtener_etiquetas_logicas("Revista Mexicana de Fisica")
        assert "Emergente" in etiquetas
        assert "Rapida" in etiquetas
        assert "Alto Impacto" not in etiquetas

    def test_etiquetado_inexistente(self):
        """Una revista inexistente no debe tener etiquetas."""
        etiquetas = _obtener_etiquetas_logicas("Inexistente Journal")
        assert etiquetas == []


# ============================================================
# TESTS: aplicar_reglas (Core logic pipeline)
# ============================================================

class TestAplicarReglas:
    """Verifica el filtrado logico principal con diferentes criterios."""

    def test_sin_preferencias(self):
        """Sin preferencias, debe devolver todas las revistas con sus etiquetas."""
        res = aplicar_reglas({})
        assert len(res) == len(base_datos)
        for r in res:
            assert "etiquetas_logicas" in r

    def test_filtrado_area_exacta(self):
        """Filtrar por area exacta (ej. fisica) debe incluir fisica y multidisciplinarias."""
        res = aplicar_reglas({"area": "fisica"})
        areas = set(r["area"] for r in res)
        # Debe contener fisica y multidisciplinaria
        assert "fisica" in areas
        assert "multidisciplinaria" in areas
        # No debe contener computacion
        assert "ciencias de la computacion" not in areas

    def test_filtrado_indexacion(self):
        """Filtrar por indexacion especifica."""
        res = aplicar_reglas({"indexacion": "scopus q1"})
        assert len(res) > 0
        for r in res:
            assert r["indexacion"] == "scopus q1"

    def test_filtrado_apc(self):
        """Filtrar por cobro de APC."""
        res = aplicar_reglas({"apc": "no"})
        assert len(res) > 0
        for r in res:
            assert r["apc"] == "no"

    def test_filtrado_num_tiempo(self):
        """Filtrar por tiempo de revision maximo."""
        res = aplicar_reglas({"tiempo_max": "3"})
        assert len(res) > 0
        for r in res:
            assert r["tiempo_revision"] <= 3

    def test_filtrado_num_impacto(self):
        """Filtrar por factor de impacto minimo."""
        res = aplicar_reglas({"impacto_min": "10.0"})
        assert len(res) > 0
        for r in res:
            assert r["factor_impacto"] >= 10.0

    def test_filtrado_complejo_vacio(self):
        """Criterios demasiado estrictos deben devolver una lista vacia."""
        res = aplicar_reglas({
            "area": "linguistica",
            "indexacion": "scopus q1",
            "impacto_min": "50.0"
        })
        assert res == []

    def test_filtrado_invalid_numeric(self):
        """Filtros numericos mal formateados no deben colapsar el programa."""
        res = aplicar_reglas({
            "tiempo_max": "invalido",
            "impacto_min": "deberia_fallar"
        })
        assert len(res) == len(base_datos)  # Ignora filtros invalidos y devuelve todas


# ============================================================
# TESTS: Auxiliares
# ============================================================

def test_obtener_areas_disponibles():
    """Verifica la obtencion de areas tematicas unicas."""
    areas = obtener_areas_disponibles()
    assert isinstance(areas, list)
    assert len(areas) > 0
    assert "multidisciplinaria" in areas
    assert areas == sorted(list(set(areas)))


def test_obtener_indexaciones_disponibles():
    """Verifica la obtencion de indexaciones unicas."""
    idx = obtener_indexaciones_disponibles()
    assert isinstance(idx, list)
    assert len(idx) > 0
    assert "scopus q1" in idx
    assert idx == sorted(list(set(idx)))


def test_fallback_igualdad():
    """Verifica que el modo fallback de los mismos resultados que el modo normal."""
    prefs = {"area": "fisica", "indexacion": "scopus q2", "apc": "no"}
    normal = aplicar_reglas(prefs)
    fallback = _filtrar_fallback(prefs)
    
    nombres_normal = sorted([r["nombre"] for r in normal])
    nombres_fallback = sorted([r["nombre"] for r in fallback])
    
    assert nombres_normal == nombres_fallback
