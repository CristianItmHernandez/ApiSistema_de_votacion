# Fase 4: Autenticación (Extra Opcional) y Suite de Pruebas con Pytest

## Objetivo de la Fase
Cumplir con el extra opcional de seguridad (Autenticación JWT / Basic Auth) sin entorpecer la evaluación de los endpoints principales, y construir una suite de pruebas automatizadas que valide todas las restricciones del sistema.

---

## 1. Archivos a Crear en esta Fase

```text
app/
└── auth/
    ├── __init__.py
    └── security.py
tests/
├── __init__.py
├── conftest.py
└── test_voting_system.py
```

---

## 2. Especificaciones de Seguridad (`app/auth/security.py`)

Para facilitar tanto la revisión rápida como la demostración del extra de seguridad:
1. Implementar **Autenticación JWT (Bearer Token)**:
   * Endpoint `POST /auth/token` que recibe credenciales de administrador (configuradas en variables de entorno, por defecto `admin` / `admin123`) y devuelve un `access_token` JWT firmado con `HS256`.
2. Configurar una variable de entorno `AUTH_ENABLED: bool = False` (o proteger endpoints administrativos específicos / incluir un endpoint de verificación) o exigir el token cuando se envíe, documentando claramente en el `README.md` y en Swagger (`/docs` mediante `OAuth2PasswordBearer`) cómo autenticarse con un clic.

---

## 3. Suite de Pruebas (`tests/test_voting_system.py`)

Configurar `conftest.py` con una base de datos SQLite en memoria (`sqlite:///:memory:`) para que las pruebas sean aisladas y ultrarrápidas.

### Casos de Prueba Obligatorios:
1. **`test_register_voter_success`:** Crea un votante y verifica que `has_voted` sea `False`.
2. **`test_register_candidate_success`:** Crea un candidato y verifica que `votes` sea `0`.
3. **`test_voter_cannot_be_candidate`:** Crea un votante llamado `"Carlos Ruiz"` e intenta crear un candidato `"carlos ruiz"`. Verifica que devuelva `400 Bad Request`.
4. **`test_candidate_cannot_be_voter`:** Crea una candidata llamada `"Elena Diaz"` e intenta crear un votante con el nombre `"Elena Diaz"`. Verifica que devuelva `400 Bad Request`.
5. **`test_cast_vote_and_integrity`:** Crea votante y candidato, emite voto en `POST /votes`, y comprueba que `voter.has_voted == True` y `candidate.votes == 1`.
6. **`test_prevent_double_voting`:** Intenta emitir un segundo voto con el mismo `voter_id` y comprueba que devuelva `400 Bad Request`.
7. **`test_cannot_delete_voter_who_voted`:** Intenta hacer `DELETE /voters/{id}` de un votante que ya votó y verifica que devuelva `409 Conflict`.
8. **`test_statistics_and_chart_generation`:** Consulta `GET /votes/statistics` (verificando el porcentaje exacto) y `GET /votes/statistics/chart` (verificando `status_code == 200` y `content-type == "image/png"`).

---

## 4. Criterios de Aceptación (Definition of Done)
- [ ] Al ejecutar `pytest -v` en la raíz del proyecto, todos los tests pasan en verde (`8 passed`).
- [ ] El botón **Authorize** aparece correctamente en el Swagger UI (`/docs`).