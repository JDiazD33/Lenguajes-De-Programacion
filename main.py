"""Punto de entrada principal de la aplicacion web.

Este modulo:
1. Crea la instancia de la aplicacion Flask.
2. Configura el directorio de plantillas (ui/).
3. Registra el blueprint del controlador.
4. Inicia el servidor de desarrollo.

Ejecutar con: python main.py
"""

from flask import Flask
from controller import main_bp

app = Flask(__name__, template_folder="ui")
app.secret_key = "recomendacion-revistas-multiparadigma-segura-2024"
app.register_blueprint(main_bp)

if __name__ == "__main__":
    print("=" * 60)
    print("SISTEMA DE RECOMENDACION MULTIPARADIGMA DE REVISTAS")
    print("=" * 60)
    print("Integracion de 3 paradigmas:")
    print("  [1] Imperativo/OOP  -> controller.py")
    print("  [2] Funcional       -> processor.py")
    print("  [3] Logico (kanren) -> logic_rules.py")
    print("-" * 60)
    print("Servidor iniciado en: http://127.0.0.1:5000")
    print("Presione CTRL+C para detener.")
    print("=" * 60)
    app.run(debug=True, port=5000)
