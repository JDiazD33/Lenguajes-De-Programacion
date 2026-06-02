# Sistema de Recomendacion de Revistas Cientificas (Multiparadigma)

Sistema web que integra tres paradigmas de programacion (Imperativo/OOP, Funcional, Logico)
para recomendar revistas academicas donde publicar articulos de investigacion.

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

## Dependencias

- **Python 3.11+**
- **Flask** >= 3.0.0 (framework web)
- **kanren** >= 1.0.0 (programacion logica)

## Instalacion

### 1. Clonar o copiar el proyecto

```bash
cd ruta/del/proyecto/PP
```

### 2. Crear y activar entorno virtual (recomendado)

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

Esto instalara:
- Flask
- kanren (libreria de programacion logica para Python)

## Ejecucion

```bash
python main.py
```

El servidor se iniciara en: **http://127.0.0.1:5000**

Abra esa URL en su navegador para usar el sistema.

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
