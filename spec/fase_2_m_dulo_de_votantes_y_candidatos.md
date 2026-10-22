# Fase 2: Gestión de Votantes, Candidatos y Validación Cruzada

## Objetivo de la Fase
Implementar la lógica de negocio y los endpoints REST para registrar, listar (con paginación y filtros) y eliminar votantes y candidatos, garantizando la restricción fundamental: **un votante no puede ser candidato y viceversa**.

---

## 1. Archivos a Crear/Modificar en esta Fase

```text
app/
├── services/
│   ├── __init__.py
│   ├── voter_service.py
│   └── candidate_service.py
├── routers/
│   ├── __init__.py
│   ├── voters.py
│   └── candidates.py
└── main.py
```

---

## 2. Reglas de Negocio a Implementar (`services/`)

### 2.1. Servicio de Votantes (`voter_service.py`)
1. **Crear Votante (`create_voter`):**
   * Normalizar el nombre: `clean_name = data.name.strip().lower()`.
   * **Validación Cruzada:** Consultar en `Candidate` si existe un registro donde `func.lower(func.trim(Candidate.name)) == clean_name`. Si existe $\rightarrow$ lanzar `HTTPException(status_code=400, detail="Un candidato registrado no puede ser inscrito como votante.")`.
   * **Validación de Email Único:** Consultar en `Voter` si ya existe el `email`. Si existe $\rightarrow$ lanzar `HTTPException(status_code=409, detail="El correo electrónico ya está registrado.")`.
   * Guardar el votante con `has_voted = False`.
2. **Listar Votantes (`get_voters`):**
   * Soportar parámetros opcionales: `skip: int = 0`, `limit: int = 10`, `has_voted: bool | None = None`, `search: str | None = None`.
3. **Eliminar Votante (`delete_voter`):**
   * Buscar votante por `id`. Si no existe $\rightarrow$ `404 Not Found`.
   * Si `voter.has_voted == True` $\rightarrow$ lanzar `HTTPException(status_code=409, detail="No se puede eliminar un votante que ya ha emitido su voto.")`.
   * Eliminar votante y confirmar cambios.

### 2.2. Servicio de Candidatos (`candidate_service.py`)
1. **Crear Candidato (`create_candidate`):**
   * Normalizar el nombre: `clean_name = data.name.strip().lower()`.
   * **Validación Cruzada:** Consultar en `Voter` si existe un registro donde `func.lower(func.trim(Voter.name)) == clean_name`. Si existe $\rightarrow$ lanzar `HTTPException(status_code=400, detail="Un votante registrado no puede ser inscrito como candidato.")`.
   * **Validación de Duplicidad:** Consultar en `Candidate` si ya existe ese nombre. Si existe $\rightarrow$ lanzar `HTTPException(status_code=409, detail="El candidato ya se encuentra registrado.")`.
   * Guardar el candidato con `votes = 0`.
2. **Listar Candidatos (`get_candidates`):**
   * Soportar parámetros opcionales: `skip: int = 0`, `limit: int = 10`, `party: str | None = None`.

---

## 3. Endpoints a Exponer (`routers/`)

* `POST /voters` (Status `201 Created`)
* `GET /voters` (Status `200 OK`) — *Incluye Extra de paginación y filtrado*
* `DELETE /voters/{id}` (Status `200 OK`)
* `POST /candidates` (Status `201 Created`)
* `GET /candidates` (Status `200 OK`) — *Incluye Extra de paginación y filtrado por partido*

---

## 4. Criterios de Aceptación (Definition of Done)
- [ ] Si registro a "Juan Perez" como votante e intento registrar a "juan perez " como candidato, el API responde `400 Bad Request`.
- [ ] Si registro a "Maria Gomez" como candidata e intento registrarla como votante, el API responde `400 Bad Request`.
- [ ] Los endpoints de listado responden correctamente a los query params `skip` y `limit`.