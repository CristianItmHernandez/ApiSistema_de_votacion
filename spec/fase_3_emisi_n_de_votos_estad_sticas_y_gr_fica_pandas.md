# Fase 3: Emisión de Votos Transaccional, Estadísticas y Gráfica con Pandas

## Objetivo de la Fase
Implementar el núcleo del sistema electoral: la emisión atómica de votos, el cálculo de estadísticas porcentuales y la generación de la gráfica de barras (Votos vs. Candidatos) utilizando `pandas` y `matplotlib`.

---

## 1. Archivos a Crear/Modificar en esta Fase

```text
app/
├── schemas/
│   └── statistics.py
├── services/
│   ├── vote_service.py
│   └── stats_service.py
└── routers/
    └── votes.py
static/
└── charts/
```

---

## 2. Especificaciones Técnicas

### 2.1. Emisión de Votos (`vote_service.py`)
* **Función `cast_vote(db: Session, vote_data: VoteCreate)`:**
  1. Buscar `Voter` por `vote_data.voter_id`. Si no existe $\rightarrow$ `404 Not Found` (`"El votante especificado no existe."`).
  2. Verificar si `voter.has_voted` es `True`. Si lo es $\rightarrow$ `400 Bad Request` (`"El votante ya ha emitido un voto previamente."`).
  3. Buscar `Candidate` por `vote_data.candidate_id`. Si no existe $\rightarrow$ `404 Not Found` (`"El candidato especificado no existe."`).
  4. **Transacción Atómica:**
     * Instanciar `new_vote = Vote(voter_id=voter.id, candidate_id=candidate.id)`.
     * Asignar `voter.has_voted = True`.
     * Incrementar `candidate.votes += 1`.
     * Hacer `db.add(new_vote)` y `db.commit()`. (Envolver en `try/except` con `db.rollback()` en caso de error inesperado).

### 2.2. Estadísticas de Votación (`stats_service.py`)
* **Función `get_voting_statistics(db: Session)`:**
  * Consultar todos los candidatos y el conteo total de votantes que han votado (`Voter.has_voted == True`).
  * Calcular para cada candidato:
    $$\text{percentage} = \text{round}\left(\left(\frac{\text{candidate.votes}}{\text{total\_voters\_voted}}\right) \times 100, 2\right)$$
    *(Si `total_voters_voted == 0`, entonces `percentage = 0.0`)*.
  * Retornar objeto estructurado con:
    * `total_voters_voted`: int
    * `results_by_candidate`: lista con `candidate_id`, `name`, `party`, `votes`, `percentage`.

### 2.3. Gráfica con Pandas (`stats_service.py`)
* **Función `generate_votes_chart(db: Session) -> str`:**
  * Extraer la lista de candidatos (`name`, `votes`) desde la base de datos.
  * Crear un `pd.DataFrame` de **Pandas** con las columnas `["Candidato", "Votos"]`.
  * Utilizar el DataFrame de Pandas junto con `matplotlib.pyplot` para graficar el estado actual de los votos:
    * Eje X: Candidatos (`df["Candidato"]`).
    * Eje Y: Cantidad de Votos (`df["Votos"]`).
    * Mostrar etiqueta numérica exacta sobre cada barra.
  * Guardar la imagen en `static/charts/voting_results.png` y devolver la ruta para ser servida con `FileResponse(path, media_type="image/png")`.

---

## 3. Endpoints a Exponer (`routers/votes.py`)

* `POST /votes` (Status `201 Created`): Emitir un voto.
* `GET /votes` (Status `200 OK`): Obtener todos los votos emitidos.
* `GET /votes/statistics` (Status `200 OK`): Obtener JSON con totales, porcentajes por candidato y total de votantes que han votado.
* `GET /votes/statistics/chart` (Status `200 OK`): Generar y devolver en tiempo real la imagen `.png` de la gráfica creada con Pandas.

---

## 4. Criterios de Aceptación (Definition of Done)
- [ ] Al emitir un voto válido, `has_voted` pasa a `true` y `votes` del candidato sube en `1`.
- [ ] Si el mismo `voter_id` intenta votar de nuevo, recibe `400 Bad Request` y el conteo del candidato no se altera.
- [ ] `GET /votes/statistics` funciona incluso cuando hay `0` votos emitidos (sin lanzar error de división por cero).
- [ ] `GET /votes/statistics/chart` genera el archivo `.png` usando un `DataFrame` de Pandas y muestra la imagen en el navegador o Postman.