# Arquitectura y flujo de la API de votaciones

Este documento muestra cómo una solicitud atraviesa los componentes de la API y cómo se relacionan los endpoints para registrar personas, emitir votos y consultar resultados.

## Interacción entre componentes

La API separa el transporte HTTP, las reglas de negocio y el acceso a datos. Las solicitudes llegan directamente a FastAPI, sin middleware de validación del host. Los routers reciben las solicitudes; los servicios aplican validaciones y operaciones; los modelos SQLAlchemy representan los registros persistidos.

```mermaid
flowchart LR
    Cliente["Cliente HTTP<br/>Navegador, cURL o aplicación"]
    App["FastAPI<br/>app/main.py"]
    Routers["Routers<br/>auth, voters, candidates, votes"]
    Auth["Seguridad JWT<br/>OAuth2PasswordBearer<br/>AUTH_ENABLED"]
    Schemas["Schemas Pydantic<br/>validan entrada y salida"]
    Services["Servicios<br/>reglas de negocio"]
    DbDependency["get_db()<br/>sesión por solicitud"]
    Models["Modelos SQLAlchemy<br/>Voter, Candidate, Vote"]
    Engine["Engine SQLAlchemy"]
    Database[("Base de datos<br/>SQLite o PostgreSQL")]
    Stats["Servicio de estadísticas<br/>Pandas + Matplotlib"]
    Chart[("static/charts/<br/>voting_results.png")]
    Docs["Swagger UI / ReDoc<br/>OpenAPI"]

    Cliente -->|"HTTP / JSON"| App
    App --> Routers
    Routers -->|"endpoints protegidos"| Auth
    Auth -->|"si AUTH_ENABLED=True,<br/>valida Bearer JWT"| Routers
    Routers --> Schemas
    Routers --> Services
    Services --> DbDependency
    DbDependency --> Models
    Models --> Engine
    Engine --> Database
    Services --> Stats
    Stats --> Models
    Stats -->|"genera gráfica"| Chart
    Chart -->|"FileResponse PNG"| Routers
    Routers -->|"respuesta HTTP"| Cliente
    App -.->|"documenta rutas y seguridad"| Docs
    Docs -.->|"prueba solicitudes"| Cliente
    Cliente -->|"POST /auth/token"| Routers
    Auth -->|"emite JWT"| Cliente
```

### Qué hace cada capa

| Componente | Responsabilidad |
|---|---|
| `main.py` | Crea la aplicación, registra routers y configura el esquema OpenAPI. |
| Entrada HTTP | FastAPI enruta las solicitudes directamente; no hay middleware de validación del host configurado en la aplicación. |
| `routers/` | Expone los endpoints HTTP y coordina dependencias, schemas y servicios. |
| `auth/security.py` | Emite y valida JWT. Con `AUTH_ENABLED=True`, los endpoints de votantes, candidatos y votos requieren `Authorization: Bearer <token>`. |
| `schemas/` | Valida los datos de las solicitudes y define las respuestas de la API. |
| `services/` | Aplica reglas de negocio, consultas, transacciones y generación de resultados. |
| `database.py` y `models/` | Proveen sesiones SQLAlchemy y representan votantes, candidatos y votos en la base de datos. |
| `stats_service.py` | Calcula porcentajes y genera la imagen PNG con Pandas y Matplotlib. |

## Flujo de funcionalidades y endpoints

Los endpoints de candidatos y votantes preparan los datos necesarios para emitir votos. Cada voto requiere un votante y un candidato previamente registrados. Los endpoints de listado, estadísticas y gráfica consultan la información guardada.

```mermaid
flowchart TD
    Inicio(["Inicio: cliente llama a la API"])
    AuthCheck{"¿AUTH_ENABLED=True?"}
    ObtenerToken["POST /auth/token<br/>username y password"]
    TokenValido{"¿Credenciales válidas?"}
    RecibirToken["Recibir access_token"]
    Bearer["Enviar Authorization: Bearer token"]
    SinToken["Continuar sin token"]
    RechazoAuth["401 Unauthorized"]
    Seleccion{"Seleccionar operación"}

    Inicio --> AuthCheck
    AuthCheck -->|Sí| ObtenerToken
    ObtenerToken --> TokenValido
    TokenValido -->|No| RechazoAuth
    TokenValido -->|Sí| RecibirToken
    RecibirToken --> Bearer
    Bearer --> Seleccion
    AuthCheck -->|No| SinToken
    SinToken --> Seleccion

    subgraph Candidatos["Candidatos"]
        CrearCandidato["POST /candidates/<br/>Registrar candidato"]
        ValidarCandidato{"¿Nombre libre<br/>y no es votante?"}
        GuardarCandidato["Guardar Candidate<br/>votes = 0"]
        ErrorCandidato["400: ya es votante<br/>409: candidato duplicado"]
        ListarCandidatos["GET /candidates/<br/>skip, limit, party"]
        CrearCandidato --> ValidarCandidato
        ValidarCandidato -->|Sí| GuardarCandidato
        ValidarCandidato -->|No| ErrorCandidato
    end

    subgraph Votantes["Votantes"]
        CrearVotante["POST /voters/<br/>Registrar votante"]
        ValidarVotante{"¿No es candidato<br/>y correo disponible?"}
        GuardarVotante["Guardar Voter<br/>has_voted = false"]
        ErrorVotante["400: ya es candidato<br/>409: correo duplicado"]
        ListarVotantes["GET /voters/<br/>skip, limit, has_voted, search"]
        EliminarVotante["DELETE /voters/{voter_id}"]
        VotanteVoto{"¿Existe y no ha votado?"}
        BorrarVotante["Eliminar votante"]
        ErrorEliminar["404: no existe<br/>409: ya emitió su voto"]
        CrearVotante --> ValidarVotante
        ValidarVotante -->|Sí| GuardarVotante
        ValidarVotante -->|No| ErrorVotante
        EliminarVotante --> VotanteVoto
        VotanteVoto -->|Sí| BorrarVotante
        VotanteVoto -->|No| ErrorEliminar
    end

    subgraph Votos["Votos y resultados"]
        EmitirVoto["POST /votes/<br/>voter_id y candidate_id"]
        ValidarVoto{"¿Existen votante y candidato<br/>y el votante no ha votado?"}
        Transaccion["Transacción atómica:<br/>crear Vote<br/>marcar Voter.has_voted = true<br/>incrementar Candidate.votes"]
        Rollback["Si falla: rollback<br/>500 Internal Server Error"]
        ListarVotos["GET /votes/<br/>Listar votos emitidos"]
        Estadisticas["GET /votes/statistics"]
        Calcular["Contar votantes que votaron<br/>y calcular porcentaje por candidato"]
        Grafica["GET /votes/statistics/chart"]
        GenerarGrafica["Generar PNG con Pandas<br/>y Matplotlib"]
        EmitirVoto --> ValidarVoto
        ValidarVoto -->|Sí| Transaccion
        ValidarVoto -->|No| ErrorVoto["400: ya votó<br/>404: votante o candidato inexistente"]
        Transaccion -.->|Error de BD| Rollback
        Estadisticas --> Calcular
        Grafica --> GenerarGrafica
    end

    Seleccion --> CrearCandidato
    Seleccion --> ListarCandidatos
    Seleccion --> CrearVotante
    Seleccion --> ListarVotantes
    Seleccion --> EliminarVotante
    Seleccion --> EmitirVoto
    Seleccion --> ListarVotos
    Seleccion --> Estadisticas
    Seleccion --> Grafica
    GuardarVotante -->|"voter_id disponible"| EmitirVoto
    GuardarCandidato -->|"candidate_id disponible"| EmitirVoto
    Transaccion --> Estadisticas
    Transaccion --> ListarVotos
    Transaccion --> Grafica
    Estado["GET /<br/>Health check público"]
    Seleccion --> Estado
```

### Secuencia habitual

1. Si JWT está activo, obtener un token con `POST /auth/token` y enviarlo como `Authorization: Bearer <access_token>`.
2. Registrar un candidato con `POST /candidates/` y un votante con `POST /voters/`. La validación cruzada impide que una misma persona figure en ambos registros.
3. Emitir el voto con `POST /votes/`, enviando los identificadores del votante y del candidato. La operación marca al votante como participante e incrementa el conteo del candidato en una sola transacción.
4. Consultar los votos con `GET /votes/`, los porcentajes con `GET /votes/statistics` o la imagen con `GET /votes/statistics/chart`.

Los endpoints protegidos rechazan una solicitud sin token válido con `401` cuando `AUTH_ENABLED=True`. `POST /auth/token` y `GET /` permanecen públicos.
