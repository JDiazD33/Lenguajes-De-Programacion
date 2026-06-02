"""Tests para el modulo controlador y modelo de dominio OOP (controller.py).

Verifica encapsulamiento, herencia, polimorfismo, factory methods,
value objects, y la orquestacion del sistema de recomendacion.
"""

import pytest
from controller import (
    Revista,
    RevistaOpenAccess,
    RevistaPremium,
    crear_revista,
    CriterioBusqueda,
    ResultadoRecomendacion,
    SistemaRecomendacion,
)
from main import app


# ============================================================
# TESTS: Modelo de Dominio OOP (Revista y sus Subclases)
# ============================================================

class TestRevistaOOP:
    """Verifica herencia, encapsulamiento y polimorfismo en Revista."""

    def test_inicializacion_y_encapsulamiento(self):
        """Verifica que los atributos esten protegidos y legibles solo por properties."""
        r = Revista(
            nombre="Journal of Tests",
            area="ciencias",
            indexacion="q1",
            apc="no",
            tiempo_revision=3,
            factor_impacto=4.5
        )
        assert r.nombre == "Journal of Tests"
        assert r.area == "ciencias"
        assert r.indexacion == "q1"
        assert r.apc == "no"
        assert r.tiempo_revision == 3
        assert r.factor_impacto == 4.5

        # Intentar modificar una property deberia lanzar un AttributeError
        with pytest.raises(AttributeError):
            r.nombre = "Nuevo nombre"  # type: ignore

    def test_factory_method_from_dict(self):
        """Prueba la creacion de Revista desde un dict."""
        data = {
            "nombre": "Test Journal",
            "area": "computacion",
            "indexacion": "scopus",
            "apc": "si",
            "tiempo_revision": 5,
            "factor_impacto": 2.1
        }
        r = Revista.from_dict(data)
        assert r.nombre == "Test Journal"
        assert r.to_dict() == data

    def test_polimorfismo_y_herencia_open_access(self):
        """Verifica comportamiento polimorfico de RevistaOpenAccess."""
        data = {
            "nombre": "Open Access Journal",
            "area": "fisica",
            "indexacion": "scielo",
            "apc": "no",
            "tiempo_revision": 2,
            "factor_impacto": 1.5
        }
        r = crear_revista(data)
        assert isinstance(r, RevistaOpenAccess)
        assert isinstance(r, Revista)
        assert r.descripcion_acceso() == "Publicacion gratuita (sin APC)"
        assert r.calcular_factor_accesibilidad() == 1.0

    def test_polimorfismo_y_herencia_premium(self):
        """Verifica comportamiento polimorfico de RevistaPremium."""
        data = {
            "nombre": "Premium Journal",
            "area": "medicina",
            "indexacion": "scopus q1",
            "apc": "si",
            "tiempo_revision": 8,
            "factor_impacto": 12.4
        }
        r = crear_revista(data)
        assert isinstance(r, RevistaPremium)
        assert isinstance(r, Revista)
        assert r.descripcion_acceso() == "Requiere pago de APC (Article Processing Charge)"
        assert r.calcular_factor_accesibilidad() == 0.7

    def test_representaciones_texto(self):
        """Verifica metodos magicos __repr__ y __str__."""
        r = Revista("A", "B", "C", "no", 3, 1.2)
        assert repr(r) == "Revista('A', area='B', FI=1.2)"
        assert str(r) == "A (B)"


# ============================================================
# TESTS: Value Object (CriterioBusqueda)
# ============================================================

class TestCriterioBusqueda:
    """Verifica que el Value Object valide y encapsule correctamente las preferencias."""

    def test_normalizacion_de_valores(self):
        """Valida que normalice los textos a minusculas y limpie espacios."""
        c = CriterioBusqueda(
            area="  Computacion  ",
            indexacion="  SCOPUS q1  ",
            apc="  SI  ",
            tiempo_max="  5  ",
            impacto_min="  2.5  ",
            palabras_clave="  machine, learning  "
        )
        assert c.area == "computacion"
        assert c.indexacion == "scopus q1"
        assert c.apc == "si"
        assert c.palabras_clave == "machine, learning"

    def test_factory_method_from_form(self):
        """Simula request.form y crea CriterioBusqueda."""
        form_mock = {
            "area": "Fisica",
            "indexacion": "Cualquier",
            "apc": "no",
            "tiempo_max": "12",
            "impacto_min": "1.0",
            "palabras_clave": "optica"
        }
        c = CriterioBusqueda.from_form(form_mock)
        assert c.area == "fisica"
        assert c.indexacion == "cualquier"
        assert c.apc == "no"
        assert c.to_dict()["tiempo_max"] == "12"


# ============================================================
# TESTS: ResultadoRecomendacion
# ============================================================

class TestResultadoRecomendacion:
    """Verifica el calculo interno de estadisticas e inmutabilidad en resultados."""

    def test_estadisticas_con_elementos(self):
        """Prueba calculos de promedio y maximo puntaje."""
        criterios = CriterioBusqueda()
        revistas = [
            {"nombre": "R1", "puntaje_total": 0.8},
            {"nombre": "R2", "puntaje_total": 0.6},
            {"nombre": "R3", "puntaje_total": 0.4},
        ]
        res = ResultadoRecomendacion(criterios, revistas, "2026-06-02 12:00:00")
        assert res.total == 3
        assert res.tiene_resultados is True
        stats = res.estadisticas
        assert stats["total_candidatos"] == 3
        assert stats["promedio_puntaje"] == 0.6
        assert stats["max_puntaje"] == 0.8

    def test_estadisticas_vacias(self):
        """Prueba con 0 resultados recomendados."""
        criterios = CriterioBusqueda()
        res = ResultadoRecomendacion(criterios, [], "2026-06-02 12:00:00")
        assert res.total == 0
        assert res.tiene_resultados is False
        stats = res.estadisticas
        assert stats["total_candidatos"] == 0
        assert stats["promedio_puntaje"] == 0
        assert stats["max_puntaje"] == 0

    def test_inmutabilidad_de_lista(self):
        """Verifica que el objeto no exponga la lista interna directamente mutable."""
        criterios = CriterioBusqueda()
        lista_original = [{"nombre": "R1", "puntaje_total": 0.8}]
        res = ResultadoRecomendacion(criterios, lista_original, "timestamp")
        
        # Modificar la lista que retorna no deberia alterar la lista interna del objeto
        lista_retornada = res.revistas
        lista_retornada.append({"nombre": "R2", "puntaje_total": 0.9})
        
        assert res.total == 1

    def test_historial_entry(self):
        """Verifica el formato del diccionario para el historial."""
        criterios = CriterioBusqueda(area="fisica")
        revistas = [{"nombre": "R1", "puntaje_total": 0.8}]
        res = ResultadoRecomendacion(criterios, revistas, "time")
        entry = res.to_historial_entry()
        assert entry["preferencias"]["area"] == "fisica"
        assert entry["total_candidatos"] == 1
        assert entry["timestamp"] == "time"
        assert entry["mensaje"] is None


# ============================================================
# TESTS: SistemaRecomendacion (Core OOP orchestrator)
# ============================================================

class TestSistemaRecomendacion:
    """Verifica el ciclo de vida del orquestador, historial y mutabilidad de estado."""

    def test_estado_inicial(self):
        """Valida estado limpio al instanciarse."""
        sys = SistemaRecomendacion()
        assert sys.total_consultas == 0
        assert sys.historial == []
        assert sys.obtener_ultimo_resultado() is None

    def test_flujo_recomendar_exito(self):
        """Verifica la ejecucion completa del pipeline y adicion a historial."""
        sys = SistemaRecomendacion()
        criterios = CriterioBusqueda(area="fisica", palabras_clave="physics")
        
        resultado = sys.recomendar(criterios)
        assert isinstance(resultado, ResultadoRecomendacion)
        assert sys.total_consultas == 1
        
        last = sys.obtener_ultimo_resultado()
        assert last is not None
        assert last["preferencias"]["area"] == "fisica"
        assert last["total_candidatos"] > 0
        
        # Verificar que la revista devuelta este enriquecida
        revista_top = resultado.revistas[0]
        assert "puntaje_total" in revista_top
        assert "puntajes_parciales" in revista_top
        assert "etiquetas_logicas" in revista_top

    def test_flujo_recomendar_sin_resultados(self):
        """Verifica comportamiento cuando ninguna revista cumple las condiciones."""
        sys = SistemaRecomendacion()
        # Filtro imposible para asegurar 0 resultados
        criterios = CriterioBusqueda(area="linguistica", indexacion="scopus q1", impacto_min="100.0")
        
        resultado = sys.recomendar(criterios)
        assert resultado.total == 0
        assert sys.total_consultas == 1
        
        last = sys.obtener_ultimo_resultado()
        assert last is not None
        assert "NINGUNA revista cumple los criterios estrictos." in last["mensaje"]

    def test_limpiar_historial(self):
        """Valida vaciado del historial."""
        sys = SistemaRecomendacion()
        c = CriterioBusqueda()
        sys.recomendar(c)
        assert sys.total_consultas == 1
        
        sys.limpiar_historial()
        assert sys.total_consultas == 0
        assert sys.historial == []


# ============================================================
# TESTS: Web / Flask Integration
# ============================================================

class TestFlaskIntegration:
    """Verifica las respuestas del Blueprint Flask utilizando test_client."""

    def test_index_get(self):
        """Verifica que la pagina principal cargue con HTTP 200."""
        with app.test_client() as client:
            response = client.get("/")
            assert response.status_code == 200
            # Debe contener elementos del formulario
            assert b"Sistema de Recomendacion de Revistas Cientificas" in response.data
            assert b"Palabras Clave del Articulo" in response.data

    def test_index_post_recomendacion(self):
        """Verifica que el POST procese y devuelva resultados."""
        with app.test_client() as client:
            post_data = {
                "area": "fisica",
                "indexacion": "cualquier",
                "apc": "cualquier",
                "tiempo_max": "",
                "impacto_min": "",
                "palabras_clave": "physics"
            }
            response = client.post("/", data=post_data)
            assert response.status_code == 200
            # Debe mostrar las recomendaciones
            assert b"Resultados de la Recomendacion" in response.data
            assert b"Revistas candidatas" in response.data
