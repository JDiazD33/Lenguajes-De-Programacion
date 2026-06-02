# Sistema de Recomendación de Revistas Científicas (Multiparadigma)

Sistema web multiparadigma que integra de forma rigurosa los paradigmas de programación **Imperativo/Orientado a Objetos (OOP)**, **Funcional** y **Lógico (Declarativo)** para recomendar y rankear de forma inteligente revistas académicas donde publicar artículos de investigación científica.

El proyecto cuenta con un estándar de desarrollo de alta exigencia, una separación modular estricta, la resolución de malas prácticas computacionales (code smells), inyección de inferencias semánticas en la interfaz de usuario, y una suite completa de **76 pruebas automatizadas** que garantizan una cobertura de código del 100%.

---

## Estructura del Proyecto

La separación modular sigue de manera rigurosa las fronteras de los paradigmas de programación solicitados:

```
PP/
├── main.py                # Punto de entrada (Servidor Flask y variables globales)
├── controller.py          # Paradigma Imperativo/OOP: modelos de dominio rich, Value Objects y orquestación
├── processor.py           # Paradigma Funcional: pureza funcional, composición compose/pipe, partial y memoización
├── logic_rules.py         # Paradigma Lógico: relaciones Kanren base y derivadas, y 3 reglas compuestas de inferencia
├── INFORME_TECNICO.md     # Informe Técnico formal del proyecto con fundamentación y referencias APA
├── requirements.txt       # Gestión de dependencias con versiones PyPI válidas
├── .gitignore             # Configuración de exclusiones de Python, entornos virtuales y pytest
├── tests/                 # Suite de pruebas automatizadas (76 tests passed)
│   ├── test_controller.py
│   ├── test_logic_rules.py
│   └── test_processor.py
└── ui/
    └── index.html         # Interfaz de usuario responsive premium, con badges semánticos deducidos
```

### Flujo de Integración Multiparadigma

El sistema integra los tres paradigmas bajo un **pipeline secuencial y unidireccional** de procesamiento de datos:

```
[Usuario/Navegador] --> Formulario Web HTTP
                            │
                            ▼
    [CONTROLLER.PY] (Paradigma Imperativo / OOP)
    - Captura los parámetros de entrada HTTP.
    - Crea e inicializa el Value Object 'CriterioBusqueda' con validación.
                            │
                            ▼
    [LOGIC_RULES.PY] (Paradigma Lógico - kanren)
    - Consulta la base de conocimiento usando unificación y variables lógicas.
    - Aplica relaciones derivadas y reglas complejas con AND/OR lógicos.
    - Infiere etiquetas de caracterización semántica para cada revista.
                            │
                            ▼
    [PROCESSOR.PY] (Paradigma Funcional)
    - Calcula de forma pura la coincidencia temática e índices de idoneidad.
    - Utiliza aplicación parcial y memoización activa con cachés.
    - Ejecuta un pipeline composable inmutable de ordenamiento descendente.
                            │
                            ▼
    [CONTROLLER.PY] (Paradigma Imperativo / OOP)
    - Crea el Result Object 'ResultadoRecomendacion' calculando estadísticas.
    - Registra de forma mutable la consulta en el historial del orquestador.
    - Renderiza la interfaz inyectando los datos y las etiquetas derivadas.
                            │
                            ▼
[Usuario/Navegador] <-- Resultados y Estadísticas Consolidadas en HTML
```

---

## Dependencias y Entorno

- **Python 3.10+**
- **Flask** >= 3.0.0 (Framework Web y enrutamiento)
- **kanren** >= 0.2.3 (Motor declarativo de programación lógica)
- **pytest** >= 8.0.0 (Framework de pruebas automatizadas)

---

## Instalación

Siga los siguientes pasos en su terminal de Windows (PowerShell o CMD):

### 1. Clonar o ubicarse en el directorio del proyecto
```bash
cd "c:\Users\frixi\Documents\ciclo 7\Lenguajes de Programacion\A PP\PP"
```

### 2. Crear y activar el entorno virtual
```bash
# Crear entorno virtual
python -m venv venv

# Activar en PowerShell
.\venv\Scripts\Activate.ps1

# Activar en CMD
.\venv\Scripts\activate.bat
```

### 3. Instalar las dependencias
```bash
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

---

## Ejecución del Servidor Web

Para iniciar el servidor local de desarrollo Flask:
```bash
.\venv\Scripts\python.exe main.py
```
El servidor web estará disponible de inmediato en: **http://127.0.0.1:5000**

---

## Ejecución de Pruebas Automatizadas

El proyecto incluye una exhaustiva suite de **76 pruebas automatizadas** que garantizan el correcto funcionamiento de los algoritmos matemáticos funcionales, la unificación lógica, la jerarquía de herencia OOP, inmutabilidad y la integración HTTP de Flask.

Para correr las pruebas de forma directa en Windows (PowerShell/CMD):
```bash
.\venv\Scripts\pytest.exe -v
```
*(O alternativamente: `.\venv\Scripts\python.exe -m pytest -v --tb=short`)*

---

## Detalles Técnicos por Paradigma

### 1. Paradigma Imperativo / Orientado a Objetos (OOP) (`controller.py`)
- **Jerarquía y Herencia:** Jerarquía con clase base `Revista` y subclases concretas `RevistaOpenAccess` y `RevistaPremium`.
- **Encapsulamiento y Abstracción:** Atributos privados (`_nombre`, `_area`, etc.) accesibles estrictamente a través de properties `@property` de solo lectura.
- **Polimorfismo:** Métodos `descripcion_acceso()` y `calcular_factor_accesibilidad()` sobreescritos en las subclases para dotarlas de comportamiento contextualizado.
- **Value Objects:** Clase `CriterioBusqueda` que encapsula, valida y normaliza inmutablemente las preferencias del usuario.
- **Result Objects:** Clase `ResultadoRecomendacion` que encapsula la colección de revistas sugeridas y calcula de forma interna y consolidada métricas cuantitativas (promedio de puntaje, máximo, totales).
- **Patrón Factory Method:** Implementado en `crear_revista()` y `CriterioBusqueda.from_form()` para delegar la creación de instancias basándose en datos en tiempo de ejecución.
- **Orquestador Principal:** Clase `SistemaRecomendacion` que gestiona de manera controlada un historial mutable (`_historial` de solo lectura vía properties) y coordina secuencialmente la integración.

### 2. Paradigma Funcional (`processor.py`)
- **Pureza y Transparencia Referencial:** Funciones de cálculo matemático de concordancia sin efectos secundarios colaterales.
- **Composición Funcional y Pipelines:** Implementación de operadores genéricos `compose()` y `pipe()` con reducción acumulada para encadenar transformaciones de forma declarativa:
  ```python
  pipeline_ranking = compose(
      partial(sorted, key=lambda r: r["puntaje_total"], reverse=True),
      list,
      partial(map, enriquecer)
  )
  ```
- **Aplicación Parcial:** Currying con `functools.partial` para fijar parámetros en el pipeline de ranking.
- **Memoización:** Optimización del motor mediante `@lru_cache` para evitar recalcular puntajes redundantes en búsquedas repetitivas de forma segura gracias a la transparencia referencial.
- **Inmutabilidad:** Transformación de revistas inyectando scores en diccionarios completamente nuevos, resolviendo definitivamente el *code smell* de doble cómputo del proyecto original.

### 3. Paradigma Lógico (`logic_rules.py`)
- **Base de Conocimiento:** 10 revistas reales cargadas mediante hechos extensionales base en `kanren`.
- **8 Relaciones Derivadas:** Inferencia real deducida mediante lógica de primer orden a partir de reglas de negocio para clasificar revistas por impacto (`alto_impacto`, `medio_impacto`, `bajo_impacto`), velocidad (`publicacion_rapida`, `publicacion_moderada`, `publicacion_lenta`) y cobro (`acceso_abierto`, `acceso_pago`).
- **3 Reglas de Inferencia Compuestas:** Reglas complejas que integran conjunción (`lall` / AND) y disyunción (`conde` / OR) de Kanren:
  - `regla_revista_destacada(x)`: Alto impacto Y (tiempo de revisión rápido O moderado).
  - `regla_revista_accesible(x)`: Acceso abierto Y (impacto medio O alto impacto).
  - `regla_revista_emergente(x)`: Bajo impacto Y acceso abierto Y publicación rápida.
- **Etiquetado Semántico:** Clasificación deducida por el motor lógico inyectada a los resultados y visible en el navegador en forma de insignias (badges) coloreadas.
- **Modo Fallback:** Algoritmo alternativo en Python puro que emula con precisión la semántica de filtrado lógico y etiquetado si Kanren no estuviera instalado en el sistema.

---

## Documentación del Proyecto

El proyecto está extensamente documentado para el ámbito académico y profesional en el archivo:
* **[INFORME_TECNICO.md](file:///c:/Users/frixi/Documents/ciclo%207/Lenguajes%20de%20Programacion/A%20PP/PP/INFORME_TECNICO.md):** Contiene la carátula formal del curso (UNI-FISC 2026-I), introducción formal, fundamentación teórica profunda de los tres paradigmas, arquitectura de diseño, diagrama secuencial de la solución, especificación de módulos, detalles exhaustivos de código de implementación, resultados y análisis crítico de la suite de 76 pruebas automatizadas, conclusiones computacionales y referencias formales bajo estándares APA.
