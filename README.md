# Recomendador de Revistas de Ingenieria (Multiparadigma)

Sistema web que integra tres paradigmas de programacion (Imperativo/OOP, Funcional, Logico)
para recomendar revistas cientificas de **ingenieria** donde publicar articulos de investigacion.

---

## Requisitos e instalacion rapida

Antes de empezar asegurate de tener instalado lo siguiente.

### Dependencias del sistema

| Dependencia | Version minima | Proposito |
|-------------|----------------|-----------|
| Python      | 3.11+          | Lenguaje de ejecucion |
| pip         | 21+            | Gestor de paquetes de Python |
| Flask       | 3.0.0+         | Framework web (capa de presentacion) |
| kanren      | 0.3.0+         | Libreria de programacion logica (miniKanren) |

> **Opcional pero muy recomendado:** `git` para clonar el repositorio y un
> navegador moderno (Chrome, Firefox, Edge o Safari actualizado).

### Instalacion paso a paso

#### Opcion A -- Windows 10 / 11 (PowerShell o CMD)

```powershell
# 1. (Opcional) Instalar Python 3.11+ desde https://www.python.org/downloads/
#    Marcar la casilla "Add Python to PATH" durante la instalacion.

# 2. Clonar o descargar el proyecto y entrar a la carpeta
cd "C:\ruta\al\proyecto\PP"

# 3. Crear y activar un entorno virtual
python -m venv venv
.\venv\Scripts\activate

# 4. Actualizar pip e instalar dependencias
python -m pip install --upgrade pip
pip install -r requirements.txt

# 5. Ejecutar la aplicacion
python main.py
```

Tras el paso 5 abre en tu navegador: **http://127.0.0.1:5000**

Para detener el servidor pulsa `Ctrl + C` en la terminal.

#### Opcion B -- macOS 12+ (Terminal, zsh por defecto)

```bash
# 1. Instalar Python 3.11+ (recomendado via Homebrew)
#    Si no tienes Homebrew: /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python@3.11

# 2. Clonar o descargar el proyecto y entrar a la carpeta
cd /ruta/al/proyecto/PP

# 3. Crear y activar un entorno virtual
python3 -m venv venv
source venv/bin/activate

# 4. Actualizar pip e instalar dependencias
python3 -m pip install --upgrade pip
pip install -r requirements.txt

# 5. Ejecutar la aplicacion
python main.py
```

Tras el paso 5 abre en tu navegador: **http://127.0.0.1:5000**

Para detener el servidor pulsa `Ctrl + C` en la terminal.

#### Solucion de problemas frecuentes

| Problema | Solucion |
|----------|----------|
| `python: command not found` (Mac) | Usa `python3` en su lugar, o instala Python con `brew install python@3.11` |
| `python: command not found` (Windows) | Reinstala Python desde python.org marcando "Add Python to PATH" |
| `pip` no se reconoce | Ejecuta `python -m pip install -r requirements.txt` |
| `ERROR: No matching distribution found for kanren` | Verifica tu conexion a internet; `kanren 0.3.0` existe en PyPI |
| Puerto 5000 ocupado | Edita `main.py` linea final y cambia `port=5000` por otro (ej. 5050) |
| `Activate.ps1` bloqueado por politica (Windows) | Ejecuta `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` una vez |

---

## Arquitectura

```
PP/
├── main.py              # Punto de entrada (Flask)
├── controller.py        # Paradigma Imperativo/OOP: rutas, formularios, coordinacion
├── processor.py          # Paradigma Funcional: map, filter, reduce, lambdas, ranking
├── logic_rules.py        # Paradigma Logico: kanren, reglas de inferencia, base de conocimiento
├── ui/
│   └── index.html        # Interfaz web (formulario + resultados)
├── tests/
│   ├── test_controller.py
│   ├── test_processor.py
│   └── test_logic_rules.py
├── requirements.txt
├── .gitignore
└── README.md
```

### Flujo de integracion multiparadigma

```
[Investigador] --> Formulario web
                    Titulo + Resumen + Filtros
                        |
                        v
    [CONTROLLER] - Imperativo/OOP
    Recibe datos, orquesta el flujo
                        |
                        v
    [LOGIC_RULES] - Logico (kanren)
    Filtra revistas por reglas estrictas
    (indexacion, area, apc, tiempo, impacto)
    + Etiquetas logicas inferidas
                        |
                        v
    [PROCESSOR] - Funcional
    Extrae terminos del titulo/resumen (pipeline: tokenize -> filter stopwords -> dedup)
    Calcula puntajes y ranking
    (map, filter, reduce, lambdas, compose, partial)
                        |
                        v
    [CONTROLLER] - Imperativo
    Registra en historial, renderiza plantilla
                        |
                        v
[Investigador] <-- Revistas recomendadas ordenadas por puntaje
```

## Uso

1. Complete los campos del formulario:

   **Datos del articulo (lo que el profesor pide):**
   - **Titulo del articulo**: titulo completo de su investigacion
   - **Resumen del articulo**: abstract o resumen de su trabajo
   - **Palabras clave** (opcional): complementan los terminos extraidos del titulo/resumen

   **Filtros de busqueda:**
   - **Area de ingenieria**: seleccione el area de su investigacion
   - **Indexacion / Cuartil**: nivel de indexacion requerido (Scopus Q1, Q2, Scielo)
   - **Cobro de APC?**: si esta dispuesto a pagar cargos por procesamiento de articulos
   - **Revision maxima (meses)**: tiempo maximo aceptable de revision
   - **Impacto minimo**: factor de impacto minimo aceptable

2. Haga clic en **"Recomendar revistas"**

3. Revise los resultados ordenados por puntaje de coincidencia. Cada resultado muestra:
   - Ranking numerico
   - Nombre de la revista, area, tiempo de revision, factor de impacto
   - Indexacion (cuartil) y si cobra APC
   - Etiquetas logicas inferidas (Destacada, Accesible, Emergente, Alto Impacto, Rapida)
   - Puntaje total con desglose: Terminos (T), Revision (R), Impacto (I)

## Base de Conocimiento

El sistema incluye **10 revistas cientificas orientadas a ingenieria**:

| Revista | Area | Indexacion | APC | Revision | F. Impacto |
|---------|------|------------|-----|----------|------------|
| Nature | multidisciplinaria | Scopus Q1 | Si | 6 meses | 49.96 |
| Science | multidisciplinaria | Scopus Q1 | Si | 4 meses | 47.73 |
| IEEE TPAMI | ingenieria de software | Scopus Q1 | Si | 8 meses | 24.31 |
| IEEE TSE | ingenieria de software | Scopus Q1 | Si | 6 meses | 7.00 |
| J. Applied Physics | ingenieria mecanica | Scopus Q2 | No | 3 meses | 2.87 |
| PLOS ONE | multidisciplinaria | Scopus Q1 | Si | 3 meses | 3.75 |
| J. Cleaner Production | ingenieria industrial | Scopus Q1 | Si | 7 meses | 11.07 |
| Engineering Structures | ingenieria civil | Scopus Q1 | Si | 5 meses | 5.60 |
| IEEE T. Power Electronics | ingenieria electrica | Scopus Q1 | Si | 4 meses | 7.50 |
| Ingeniare | ingenieria general | Scielo | No | 4 meses | 0.50 |

## Paradigmas Implementados

### 1. Imperativo / OOP (`controller.py`)
- Clase `SistemaRecomendacion` con estado mutable (historial)
- Metodo `recomendar()` que orquesta el flujo completo
- Manejo explicito del ciclo request-response HTTP
- Modificacion de estado como efecto secundario
- Herencia y polimorfismo: `RevistaOpenAccess` y `RevistaPremium` extienden `Revista`
- Factory methods: `crear_revista()`, `CriterioBusqueda.from_form()`
- Value Object: `CriterioBusqueda` (inmutable, con validacion)
- Encapsulamiento: `@property` (solo lectura) en todas las entidades

### 2. Funcional (`processor.py`)
- Funciones puras sin efectos secundarios
- `map()` para transformar listas de revistas en listas con puntajes
- `filter()` para eliminar stopwords y keywords vacias
- `reduce()` para calcular ponderacion de puntajes parciales y deduplicacion
- `sorted()` con `key=lambda` para ordenamiento declarativo
- Composicion de funciones: `compose()` y `pipe()`
- Aplicacion parcial: `functools.partial()` (currying)
- Memoizacion: `@lru_cache` (justificada por transparencia referencial)
- **Extraccion de terminos del titulo/resumen**: pipeline funcional puro
  (tokenizar -> filtrar stopwords -> filtrar cortas -> deduplicar) sin
  dependencias externas.

### 3. Logico (`logic_rules.py`)
- `kanren.Relation` para modelar atributos de revistas como relaciones logicas
- `kanren.facts()` para poblar la base de conocimiento declarativa
- `kanren.run()` con variables logicas (`var()`) para consultas
- `kanren.conde()` para expresar disyuncion (OR) en reglas de inferencia
- `kanren.lall()` para conjuncion (AND) en reglas compuestas
- **Relaciones derivadas**: alto_impacto, medio_impacto, bajo_impacto,
  publicacion_rapida, publicacion_moderada, publicacion_lenta, acceso_abierto, acceso_pago
  (inferidas a partir de los datos numericos, no estan en los datos crudos)
- **Reglas compuestas**: revista destacada, revista accesible, revista emergente
  (combinan multiples relaciones derivadas con AND/OR)
- Separacion entre conocimiento (hechos) y control (reglas)

## Formula de Puntaje

El ranking de revistas se calcula como una suma ponderada de tres dimensiones:

```
Puntaje = (Terminos del articulo x 0.40) + (Tiempo revision x 0.30) + (Factor impacto x 0.30)
```

- **Terminos del articulo (40%)**: proporcion de terminos relevantes del
  titulo + resumen + keywords que coinciden con el nombre y area de la revista.
- **Tiempo revision (30%)**: a menor tiempo de revision, mayor puntaje.
- **Factor impacto (30%)**: a mayor factor de impacto respecto al minimo deseado, mayor puntaje.

## Pruebas (Tests)

El proyecto incluye una suite de **77 pruebas automatizadas** con `pytest` que cubren los tres modulos del sistema.

### Ejecutar los tests

```powershell
# Windows (desde la carpeta del proyecto, con el venv activado)
python -m pytest tests/ -v
```

```bash
# macOS / Linux
python3 -m pytest tests/ -v
```

Resultado esperado: `77 passed` (o mas si se anaden nuevos tests).

### Que cubren los tests

| Archivo | Modulo que prueba | Que verifica |
|---------|-------------------|--------------|
| `tests/test_controller.py` | `controller.py` (Imperativo/OOP) | Encapsulamiento, herencia, polimorfismo, factory methods, value objects, inmutabilidad, integracion Flask end-to-end, campos titulo/resumen |
| `tests/test_processor.py` | `processor.py` (Funcional) | Funciones puras, composicion (compose/pipe), aplicacion parcial (partial), memoizacion (lru_cache), inmutabilidad de listas |
| `tests/test_logic_rules.py` | `logic_rules.py` (Logico) | Hechos base, relaciones derivadas, reglas compuestas (AND/OR), etiquetado logico, filtrado por area/indexacion/APC/tiempo/impacto, modo fallback |

### Notas sobre los tests

- No requieren que el servidor Flask este corriendo; las pruebas de Flask usan el cliente de test integrado de Flask.
- Si `kanren` no esta instalado, los tests del modulo logico prueban automaticamente el modo fallback.
- Para ejecutar solo los tests de un modulo: `python -m pytest tests/test_processor.py -v`

## Notas

- Si `kanren` no esta instalado, el sistema funciona en modo fallback
  manteniendo la misma semantica de filtrado.
- Los puntajes parciales se muestran en la interfaz: T (terminos del articulo),
  R (tiempo de revision), I (factor de impacto).
- El sistema extrae terminos relevantes del **titulo y resumen** del articulo
  del investigador (limpiando stopwords en espanol e ingles), y los combina
  con las keywords manuales para maximizar la precision de la recomendacion.
