# Sistema de Recomendacion de Revistas Cientificas (Multiparadigma)

Sistema web que integra tres paradigmas de programacion (Imperativo/OOP, Funcional, Logico)
para recomendar revistas academicas donde publicar articulos de investigacion.

---

## Requisitos e instalacion rapida

Antes de empezar asegurate de tener instalado lo siguiente.

### Dependencias del sistema

| Dependencia | Version minima | Proposito |
|-------------|----------------|-----------|
| Python      | 3.11+          | Lenguaje de ejecucion (probado con 3.10.11, totalmente compatible con 3.11+) |
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
├── requirements.txt
├── INFORME_TECNICO_FINAL.md
└── README.md
```

### Flujo de integracion multiparadigma

```
[Usuario] --> Formulario web
                |
                v
    [CONTROLLER] - Imperativo/OOP
    Recibe datos, orquesta el flujo
                |
                v
    [LOGIC_RULES] - Logico (kanren)
    Filtra revistas por reglas estrictas
    (indexacion, area, apc, tiempo, impacto)
                |
                v
    [PROCESSOR] - Funcional
    Calcula puntajes y ranking
    (map, filter, reduce, lambdas)
                |
                v
    [CONTROLLER] - Imperativo
    Registra en historial, renderiza plantilla
                |
                v
[Usuario] <-- Resultados en HTML
```

## Uso

1. Complete los campos del formulario:
   - **Area Tematica**: seleccione el area de su investigacion
   - **Indexacion Deseada**: nivel de indexacion requerido (Scopus Q1, Q2, Scielo, Latindex)
   - **Acepta APC?**: si esta dispuesto a pagar cargos por procesamiento de articulos
   - **Tiempo Maximo de Revision**: en meses
   - **Factor de Impacto Minimo**: valor minimo aceptable
   - **Palabras Clave**: palabras clave de su articulo (separadas por coma)

2. Haga clic en "Buscar Revistas Recomendadas"

3. Revise los resultados ordenados por puntaje de coincidencia

## Base de Conocimiento

El sistema incluye 10 revistas cientificas reales/realistas:

| Revista | Area | Indexacion | APC | Revision | F. Impacto |
|---------|------|------------|-----|----------|------------|
| Nature | multidisciplinaria | Scopus Q1 | Si | 6 meses | 49.96 |
| Science | multidisciplinaria | Scopus Q1 | Si | 4 meses | 47.73 |
| IEEE TPAMI | ciencias de la computacion | Scopus Q1 | Si | 8 meses | 24.31 |
| Journal of Applied Physics | fisica | Scopus Q2 | No | 3 meses | 2.87 |
| Revista Mexicana de Fisica | fisica | Scielo | No | 4 meses | 0.65 |
| PLOS ONE | multidisciplinaria | Scopus Q1 | Si | 3 meses | 3.75 |
| Journal of Cleaner Production | ciencias ambientales | Scopus Q1 | Si | 7 meses | 11.07 |
| Boletin de Linguistica | linguistica | Scielo | No | 6 meses | 0.25 |
| Investigacion Bibliotecologica | bibliotecologia | Latindex | No | 4 meses | 0.45 |
| Revista Latinoamericana de Psicologia | psicologia | Latindex | No | 5 meses | 0.82 |

## Paradigmas Implementados

> Nota: el sistema integra los tres paradigmas (Imperativo/OO, Funcional y Logico)
> como se documenta en detalle en `INFORME_TECNICO_FINAL.md`. A continuacion un
> resumen ejecutivo de los modulos del proyecto.

### 1. Imperativo / OOP (`controller.py`)
- Clase `SistemaRecomendacion` con estado mutable (historial)
- Metodo `recomendar()` que orquesta el flujo completo
- Manejo explicito del ciclo request-response HTTP
- Modificacion de estado como efecto secundario

### 2. Funcional (`processor.py`)
- Funciones puras sin efectos secundarios
- `map()` para transformar listas de revistas en listas con puntajes
- `filter()` para eliminar keywords vacias
- `reduce()` para calcular ponderacion de puntajes parciales
- `sorted()` con `key=lambda` para ordenamiento declarativo
- Composicion de funciones

### 3. Logico (`logic_rules.py`)
- `kanren.Relation` para modelar atributos de revistas como relaciones logicas
- `kanren.facts()` para poblar la base de conocimiento declarativa
- `kanren.run()` con variables logicas (`var()`) para consultas
- `kanren.conde()` para expresar disyuncion (OR) en reglas de inferencia
- Separacion entre conocimiento (hechos) y control (reglas)

## Notas

- Si `kanren` no esta instalado, el sistema funciona en modo fallback
  manteniendo la misma semantica de filtrado.
- Los puntajes parciales se muestran en la interfaz: K (keywords),
  T (tiempo de revision), I (factor de impacto).
- El peso de cada dimension es: Keywords 40%, Tiempo 30%, Impacto 30%.
