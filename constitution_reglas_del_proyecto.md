# Project Constitution: Sistema de Votaciones API

Este documento (`constitution.md`) establece los principios arquitectónicos, reglas de negocio inquebrantables, convenciones de código y estándares de calidad que rigen todo el desarrollo del proyecto **Sistema de Votaciones API**. Cualquier código, prueba o documentación generada debe adherirse estrictamente a estas directrices.

---

## 1. Stack Tecnológico Oficial

* **Lenguaje:** Python 3.10+ (Uso obligatorio de *Type Hints* modernos: `list[str]`, `int | None`, etc.).
* **Framework Web:** FastAPI.
* **ORM y Base de Datos:** SQLAlchemy 2.0 (estilo declarativo moderno con `Mapped` y `mapped_column`) sobre PostgreSQL/MySQL (con soporte transparente para SQLite en desarrollo/testing).
* **Validación y Serialización:** Pydantic v2 (`ConfigDict(from_attributes=True)`).
* **Procesamiento de Datos y Gráficas:** Pandas + Matplotlib (Backend no interactivo `Agg`).
* **Seguridad:** Autenticación mediante JWT (`PyJWT` / `python-jose`) o HTTP Basic Auth nativa de FastAPI.
* **Pruebas:** Pytest + HTTPX (`TestClient`).

---

## 2. Principios Arquitectónicos (Separación de Responsabilidades)

El código debe dividirse estrictamente en 4 capas. **Está prohibido** mezclar responsabilidades:

1. **`routers/` (Capa de Presentación / Controladores HTTP):**
   * Solo define rutas, códigos de estado HTTP, inyección de dependencias (`Depends(get_db)`) y esquemas de entrada/salida.
   * **Prohibido:** Escribir consultas SQL/ORM directas o lógica de negocio compleja dentro de los routers.
2. **`services/` (Capa de Lógica de Negocio):**
   * Contiene todas las validaciones de dominio, reglas cruzadas, transacciones atómicas y cálculos con Pandas.
   * Lanza `HTTPException` claras y semánticas cuando una regla de negocio se viola.
3. **`models/` (Capa de Persistencia / ORM):**
   * Define únicamente las tablas de base de datos, claves primarias, claves foráneas, índices y restricciones (`UniqueConstraint`).
4. **`schemas/` (Capa de Contratos de Datos / DTOs):**
   * Define los modelos Pydantic para creación (`Create`), respuesta (`Response`) y estadísticas.

---

## 3. Reglas de Negocio Inquebrantables (Invariantes del Dominio)

1. **Exclusión Mutua Votante-Candidato (Validación Cruzada):**
   * Un votante **nunca** puede ser registrado como candidato, y un candidato **nunca** puede ser registrado como votante.
   * La comparación debe ser insensible a mayúsculas/minúsculas y espacios extremos: `func.lower(func.trim(Model.name)) == name.strip().lower()`.
2. **Unicidad de Voto (1 Votante = 1 Voto):**
   * Un votante con `has_voted == True` tiene estrictamente prohibido emitir otro voto.
   * Además de la validación en código, la columna `voter_id` en la tabla `votes` debe tener la restricción `UNIQUE` a nivel de base de datos.
3. **Atomicidad en la Emisión del Voto (Transacción ACID):**
   * El proceso de votar (`POST /votes`) debe ejecutar en una **única transacción de BD**:
     1. Insertar el registro en `votes`.
     2. Actualizar `voter.has_voted = True`.
     3. Incrementar `candidate.votes += 1`.
   * Si ocurre cualquier excepción, se debe ejecutar `db.rollback()` inmediatamente.
4. **Protección del Historial Electoral:**
   * No se permite eliminar un votante (`DELETE /voters/{id}`) si su campo `has_voted` es `True`. Hacerlo corrompería la auditoría de votos emitidos. Debe rechazarse con HTTP `409 Conflict`.
5. **Seguridad Matemática en Estadísticas:**
   * El cálculo de porcentajes de votación debe prevenir explícitamente la división por cero (`ZeroDivisionError`) cuando el total de votos emitidos sea `0`, devolviendo `0.0%`.

---

## 4. Estándares RESTful y Manejo de Errores

* **Códigos de Estado HTTP Obligatorios:**
  * `200 OK`: Consultas (`GET`) o eliminaciones con mensaje de retorno.
  * `201 Created`: Creación exitosa (`POST /voters`, `POST /candidates`, `POST /votes`).
  * `400 Bad Request`: Violación de regla de negocio (ej. votante intentando ser candidato, votante que ya votó).
  * `401 Unauthorized`: Credenciales o token JWT faltante/inválido en endpoints protegidos.
  * `404 Not Found`: Recurso (`voter_id` o `candidate_id`) inexistente.
  * `409 Conflict`: Duplicidad de datos únicos (ej. email repetido, candidato repetido, o intento de borrar un votante que ya votó).
  * `422 Unprocessable Entity`: Error de validación de formato (ej. email inválido, campos faltantes).
* **Formato de Respuesta de Error:**
  * Todas las excepciones deben retornar un JSON estándar: `{"detail": "Descripción clara del error en español"}`.

---

## 5. Convenciones de Código y Calidad

* **Idioma:**
  * Nombres de variables, funciones, clases, tablas, columnas y rutas en **inglés** (`Voter`, `has_voted`, `candidate_id`).
  * Mensajes de error para el usuario, documentación Swagger (`summary`, `description`) y comentarios explicativos en **español**.
* **Inyección de Dependencias:**
  * Toda sesión de base de datos debe inyectarse mediante un generador `get_db()` que garantice el cierre de la sesión en un bloque `finally`.