# Fase 5: Documentación (`README.md`), Ejemplos de Uso y Entrega

## Objetivo de la Fase
Preparar el entregable final para el repositorio público de GitHub, asegurando una documentación impecable con instrucciones paso a paso, comandos `curl` listos para copiar y pegar, y las capturas de las estadísticas y la gráfica generada con Pandas.

---

## 1. Archivos a Crear en esta Fase

```text
voting-system-api/
├── README.md
├── seed_and_chart.py   # Script auxiliar para poblar datos de prueba y generar la gráfica al instante
└── docs/
    └── images/         # Carpeta para alojar las capturas de pantalla en el README
```

---

## 2. Script de Demostración Rápida (`seed_and_chart.py`)

Crear un script ejecutable (`python seed_and_chart.py`) que:
1. Cree 3 candidatos y 10 votantes de ejemplo en la base de datos.
2. Simule la emisión de 8 votos distribuidos entre los candidatos.
3. Imprima en consola el resumen de estadísticas.
4. Invoque el servicio de **Pandas** para generar `static/charts/voting_results.png` automáticamente, permitiendo al evaluador ver la gráfica inmediatamente o tomar la captura para el `README.md`.

---

## 3. Estructura Obligatoria del `README.md`

El archivo `README.md` debe contener las siguientes secciones:

1. **Título y Descripción del Proyecto:** Resumen de la arquitectura y características implementadas (incluyendo los extras de paginación, filtrado, JWT y gráfica con Pandas).
2. **Requisitos Previos e Instalación Local:**
   * Creación del entorno virtual (`python -m venv venv`).
   * Instalación de paquetes (`pip install -r requirements.txt`).
   * Configuración de la base de datos (SQLite por defecto para pruebas inmediatas o PostgreSQL/MySQL mediante `.env`).
   * Comando para iniciar el servidor (`uvicorn app.main:app --reload`).
3. **Documentación Interactiva (Swagger UI):**
   * Enlace directo a `http://127.0.0.1:8000/docs` y `http://127.0.0.1:8000/redoc`.
4. **Ejemplos de Uso de la API (`cURL` / Postman):**
   * Bloque `curl` para registrar candidatos (`POST /candidates`).
   * Bloque `curl` para registrar votantes (`POST /voters`).
   * Bloque `curl` demostrando la validación cruzada (error al registrar un votante como candidato).
   * Bloque `curl` para emitir un voto (`POST /votes`).
   * Bloque `curl` para consultar estadísticas (`GET /votes/statistics`).
   * Bloque `curl` para descargar la gráfica (`GET /votes/statistics/chart`).
5. **Capturas de las Estadísticas y Gráfica con Pandas:**
   * Imagen incrustada de la gráfica generada: `![Estado Actual de Votaciones](static/charts/voting_results.png)`.
   * Captura de la respuesta JSON del endpoint `/votes/statistics`.
6. **Ejecución de Pruebas Automatizadas:**
   * Comando `pytest -v`.

---

## 4. Criterios de Aceptación Final (Checklist de Entrega)
- [ ] El repositorio en GitHub es público y no incluye archivos basura (`__pycache__`, `.venv`, `.env` real).
- [ ] El `README.md` se visualiza correctamente en GitHub con la imagen de la gráfica generada por Pandas visible.
- [ ] Cualquier evaluador puede clonar el repositorio y levantar el servidor en menos de 2 minutos siguiendo las instrucciones.