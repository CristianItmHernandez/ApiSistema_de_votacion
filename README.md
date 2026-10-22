# Sistema de Votaciones API

API REST construida con **FastAPI** para gestionar un proceso electoral completo: registro de votantes y candidatos con validación cruzada, emisión atómica de votos, estadísticas porcentuales y gráfica de resultados generada en tiempo real con **Pandas + Matplotlib**.

---

## Características implementadas

| Característica | Detalle |
|---|---|
| **Arquitectura en capas** | `routers/` → `services/` → `models/` + `schemas/` (sin mezcla de responsabilidades) |
| **Validación cruzada** | Un votante no puede ser candidato y viceversa (case/space insensitive) |
| **Unicidad de voto** | Restricción doble: en código y a nivel de columna `UNIQUE` en BD |
| **Transacción atómica** | `POST /votes` modifica 3 tablas en una sola transacción con `rollback` ante error |
| **Paginación y filtros** | `skip`, `limit`, `has_voted`, `search` en `/voters`; `party` en `/candidates` |
| **Estadísticas** | Porcentajes por candidato con protección frente a división por cero |
| **Gráfica con Pandas** | Barplot generado desde un `DataFrame` y servido como `image/png` |
| **Autenticación JWT** | `POST /auth/token` con HS256; `AUTH_ENABLED` flag para activar/desactivar |
| **Swagger interactivo** | Botón **Authorize** en `/docs` para probar el JWT sin salir del navegador |
| **Suite de tests** | 21 tests de integración con SQLite en memoria (`pytest -v`) |

---

## Requisitos previos

- Python **3.10+** (probado con 3.14.3)
- `git`
- Sin servidor de BD externo necesario: SQLite por defecto

---

## Instalación local (< 2 minutos)

```bash
# 1. Clonar el repositorio
git clone https://github.com/CristianItmHernandez/ApiSistema_de_votacion.git
cd voting-system-api
(O también click derecho en la carpeta 'voting-system-api' y click izquierdo en terminal, en caso de windows)

# 2. Crear y activar el entorno virtual
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. (Opcional) Configurar variables de entorno
#    Copia el archivo de ejemplo y edítalo si usas PostgreSQL
cp .env.example .env

# 5. Iniciar el servidor
uvicorn app.main:app --reload
```

El servidor queda disponible en `http://127.0.0.1:8000`.  
Las tablas se crean automáticamente en `voting_system.db` la primera vez.

---

## Configuración de base de datos

El archivo `.env.example` documenta las variables disponibles:

```env
# SQLite (por defecto — sin configuración adicional)
DATABASE_URL=sqlite:///./voting_system.db

# PostgreSQL
# DATABASE_URL=postgresql://user:pass@localhost:5432/voting_db

# Autenticación JWT (desactivada por defecto para evaluación)
# AUTH_ENABLED=True
# ADMIN_USERNAME=admin
# ADMIN_PASSWORD=admin123
# JWT_SECRET_KEY=cambia-esto-en-produccion
```

---

## Documentación interactiva

| URL | Descripción |
|---|---|
| `http://127.0.0.1:8000/docs` | Swagger UI — prueba todos los endpoints con un clic |
| `http://127.0.0.1:8000/redoc` | ReDoc — documentación de referencia navegable |

---

## Demostración rápida (seed + gráfica)

Pobla la BD con datos de ejemplo y genera la gráfica de resultados:

```bash
python seed_and_chart.py
```

Salida esperada:

```
[OK] 3 candidatos creados.
[OK] 10 votantes creados.
[OK] 8 votos emitidos.

--------------------------------------------------
  Total votantes que votaron : 8
--------------------------------------------------
  Alejandra Vidal          4 votos   50.00%  ####
  Ramon Delgado            3 votos   37.50%  ###
  Valentina Cruz           1 votos   12.50%  #
--------------------------------------------------

[OK] Grafica generada en: static/charts/voting_results.png
```

La imagen queda en `static/charts/voting_results.png`:

![Estado Actual de Votaciones](static/charts/voting_results.png)

---

## Ejemplos de uso — cURL

> Todos los ejemplos asumen el servidor corriendo en `http://127.0.0.1:8000`.  
> En Windows usa **Git Bash** o **WSL** para ejecutar `curl`. En PowerShell reemplazá las comillas simples por dobles.

### 1. Registrar un candidato

```bash
curl -X POST http://127.0.0.1:8000/candidates/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Alejandra Vidal", "party": "Partido Progresista"}'
```

Respuesta `201 Created`:
```json
{"id": 1, "name": "Alejandra Vidal", "party": "Partido Progresista", "votes": 0}
```

---

### 2. Registrar un votante

```bash
curl -X POST http://127.0.0.1:8000/voters/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Marco Polo", "email": "marco@demo.com"}'
```

Respuesta `201 Created`:
```json
{"id": 1, "name": "Marco Polo", "email": "marco@demo.com", "has_voted": false}
```

---

### 3. Validación cruzada — error esperado

Intentar registrar como candidato a alguien ya registrado como votante:

```bash
curl -X POST http://127.0.0.1:8000/candidates/ \
  -H "Content-Type: application/json" \
  -d '{"name": "marco polo", "party": "Cualquier Partido"}'
```

Respuesta `400 Bad Request`:
```json
{"detail": "Un votante registrado no puede ser inscrito como candidato."}
```

---

### 4. Emitir un voto

```bash
curl -X POST http://127.0.0.1:8000/votes/ \
  -H "Content-Type: application/json" \
  -d '{"voter_id": 1, "candidate_id": 1}'
```

Respuesta `201 Created`:
```json
{"id": 1, "voter_id": 1, "candidate_id": 1}
```

---

### 5. Consultar estadísticas

```bash
curl http://127.0.0.1:8000/votes/statistics
```

Respuesta `200 OK`:
```json
{
  "total_voters_voted": 1,
  "results_by_candidate": [
    {
      "candidate_id": 1,
      "name": "Alejandra Vidal",
      "party": "Partido Progresista",
      "votes": 1,
      "percentage": 100.0
    }
  ]
}
```

---

### 6. Descargar la gráfica generada con Pandas

```bash
# Abre la imagen directamente en el navegador
curl http://127.0.0.1:8000/votes/statistics/chart --output chart.png && open chart.png
```

O visitá directamente: `http://127.0.0.1:8000/votes/statistics/chart`

---

### 7. Autenticación JWT (extra opcional)

Obtener token:
```bash
curl -X POST http://127.0.0.1:8000/auth/token \
  -d "username=admin&password=admin123"
```

Respuesta:
```json
{"access_token": "eyJ...", "token_type": "bearer"}
```

Usar el token en un request:
```bash
curl http://127.0.0.1:8000/voters/ \
  -H "Authorization: Bearer eyJ..."
```

> Para activar protección JWT en todos los endpoints: `AUTH_ENABLED=True` en `.env`.

---

### 8. Listado con paginación y filtros

```bash
# Votantes que aún no han votado, página 2
curl "http://127.0.0.1:8000/voters/?skip=10&limit=10&has_voted=false"

# Buscar votante por nombre parcial
curl "http://127.0.0.1:8000/voters/?search=marco"

# Candidatos de un partido específico
curl "http://127.0.0.1:8000/candidates/?party=Progresista"
```

---

## Ejecución de pruebas automatizadas

```bash
# Suite completa (21 tests)
pytest -v

# Solo la suite oficial (8 tests del DoD)
pytest tests/test_voting_system.py -v
```

Resultado esperado:

```
tests/test_voting_system.py::test_register_voter_success PASSED
tests/test_voting_system.py::test_register_candidate_success PASSED
tests/test_voting_system.py::test_voter_cannot_be_candidate PASSED
tests/test_voting_system.py::test_candidate_cannot_be_voter PASSED
tests/test_voting_system.py::test_cast_vote_and_integrity PASSED
tests/test_voting_system.py::test_prevent_double_voting PASSED
tests/test_voting_system.py::test_cannot_delete_voter_who_voted PASSED
tests/test_voting_system.py::test_statistics_and_chart_generation PASSED

========================= 8 passed in 1.49s =========================
```

---

## Estructura del proyecto

```
voting-system-api/
├── .env.example              # Variables de entorno documentadas
├── .gitignore
├── requirements.txt
├── seed_and_chart.py         # Demo rápida: seed + gráfica Pandas
├── app/
│   ├── main.py               # FastAPI app + registro de routers
│   ├── config.py             # Settings con pydantic-settings
│   ├── database.py           # engine, SessionLocal, Base, get_db()
│   ├── auth/
│   │   └── security.py       # JWT HS256 + dependencia get_current_admin
│   ├── models/               # ORM SQLAlchemy 2.0 (Voter, Candidate, Vote)
│   ├── schemas/              # Pydantic v2 DTOs (Create, Response, Statistics)
│   ├── services/             # Lógica de negocio (validaciones, transacción ACID)
│   └── routers/              # Endpoints HTTP (solo routing, sin lógica)
├── tests/
│   ├── conftest.py           # Fixtures compartidos (BD en memoria)
│   ├── test_voting_system.py # 8 casos DoD (Fase 4)
│   └── test_fase2_fase3.py   # 13 casos de integración (Fases 2 y 3)
├── static/
│   └── charts/               # Gráficas PNG generadas en runtime
└── docs/
    └── images/               # Capturas para el README
```

---

## Stack tecnológico

| Componente | Tecnología |
|---|---|
| Framework web | FastAPI |
| ORM | SQLAlchemy 2.0 (`Mapped`, `mapped_column`) |
| Validación | Pydantic v2 (`ConfigDict(from_attributes=True)`) |
| Base de datos | SQLite (dev) / PostgreSQL o MySQL (prod) |
| Análisis de datos | Pandas + Matplotlib (backend `Agg`) |
| Seguridad | PyJWT (HS256) + OAuth2PasswordBearer |
| Tests | Pytest + HTTPX / Starlette TestClient |
| Python | 3.10+ (type hints modernos: `list[str]`, `int \| None`) |
