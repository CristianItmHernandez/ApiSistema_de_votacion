# Fase 1: Configuración del Proyecto, Base de Datos y Modelos ORM

## Objetivo de la Fase
Establecer los cimientos del proyecto, configurar las dependencias, la conexión a la base de datos con SQLAlchemy 2.0 y definir las 3 entidades principales (`Voter`, `Candidate`, `Vote`) junto con sus esquemas Pydantic.

---

## 1. Archivos a Crear en esta Fase

```text
voting-system-api/
├── .env.example
├── requirements.txt
└── app/
    ├── __init__.py
    ├── config.py
    ├── database.py
    ├── models/
    │   ├── __init__.py
    │   ├── voter.py
    │   ├── candidate.py
    │   └── vote.py
    └── schemas/
        ├── __init__.py
        ├── voter.py
        ├── candidate.py
        └── vote.py
```

---

## 2. Especificaciones Técnicas

### 2.1. Dependencias (`requirements.txt`)
* `fastapi`
* `uvicorn[standard]`
* `sqlalchemy>=2.0.0`
* `pydantic[email]>=2.0.0`
* `pydantic-settings`
* `psycopg2-binary` (o `pymysql` si se usa MySQL)
* `pandas`
* `matplotlib`
* `pyjwt`
* `pytest`
* `httpx`

### 2.2. Configuración y Base de Datos (`app/config.py` y `app/database.py`)
* Configurar `DATABASE_URL` leyendo desde variables de entorno (por defecto `sqlite:///./voting_system.db` para facilitar la ejecución local inmediata, pero compatible con PostgreSQL `postgresql://user:pass@localhost:5432/voting_db`).
* Crear `engine`, `SessionLocal`, clase base `Base` y la dependencia `get_db()`.

### 2.3. Modelos ORM (`app/models/`)
1. **`Voter` (`voters`):**
   * `id`: `Integer`, Primary Key, autoincremental.
   * `name`: `String(150)`, `nullable=False`, indexado.
   * `email`: `String(150)`, `nullable=False`, `unique=True`, indexado.
   * `has_voted`: `Boolean`, `nullable=False`, `default=False`.
2. **`Candidate` (`candidates`):**
   * `id`: `Integer`, Primary Key, autoincremental.
   * `name`: `String(150)`, `nullable=False`, `unique=True`, indexado.
   * `party`: `String(100)`, `nullable=True`.
   * `votes`: `Integer`, `nullable=False`, `default=0`.
3. **`Vote` (`votes`):**
   * `id`: `Integer`, Primary Key, autoincremental.
   * `voter_id`: `Integer`, `ForeignKey("voters.id")`, `nullable=False`, `unique=True`.
   * `candidate_id`: `Integer`, `ForeignKey("candidates.id")`, `nullable=False`.

### 2.4. Esquemas Pydantic (`app/schemas/`)
* **`VoterCreate`:** `name` (str, min_length=2), `email` (`EmailStr`).
* **`VoterResponse`:** `id`, `name`, `email`, `has_voted`.
* **`CandidateCreate`:** `name` (str, min_length=2), `party` (`str | None = None`).
* **`CandidateResponse`:** `id`, `name`, `party`, `votes`.
* **`VoteCreate`:** `voter_id` (`int`), `candidate_id` (`int`).
* **`VoteResponse`:** `id`, `voter_id`, `candidate_id`.

---

## 3. Criterios de Aceptación (Definition of Done)
- [ ] Las tablas se crean automáticamente al iniciar la aplicación con `Base.metadata.create_all(bind=engine)`.
- [ ] Los esquemas Pydantic validan que el correo de un votante tenga formato válido (`EmailStr`) y que los nombres no sean cadenas vacías o de puros espacios.