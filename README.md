# RecoCore

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.116.1-009688)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.x-red)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)
![Tests](https://img.shields.io/badge/tests-pytest-green)

RecoCore is a production-style ecommerce recommendation engine API built with FastAPI, PostgreSQL, SQLAlchemy 2.x, Docker, and Docker Compose.

The project demonstrates backend engineering fundamentals through clean API design, SQLAlchemy ORM models, service-layer separation, and recommendation ranking logic implemented without machine learning.

## Goals

- Demonstrate backend engineering skills with a realistic API project.
- Implement recommendation algorithms without machine learning.
- Showcase clean architecture, service layers, and ranking logic.
- Provide test coverage around recommendation behavior and API correctness.

## Tech Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy 2.x, synchronous ORM
- Docker
- Docker Compose
- Pytest

## Features

- Interaction tracking for ecommerce user behavior.
- Trending recommendations ranked by aggregate interaction weight.
- Optional category filtering for trending recommendations.
- Decay scoring so recent interactions have stronger influence.
- Category affinity scoring based on user interaction history.
- Personalized recommendations based on primary and secondary user interests.
- Exclusion logic for liked, shared, and purchased items.
- Viewed items remain eligible for future recommendations.
- Cold-start support through trending recommendations.

## Architecture

RecoCore separates API, business logic, ranking logic, database access, and schemas into focused modules.

```text
app/
├── models/
├── routes/
├── services/
├── ranking_engine/
├── core/
├── main.py
├── db.py
└── config.py
```

### Layer Responsibilities

- `routes/`: FastAPI route definitions and request/response handling.
- `services/`: Application service layer that coordinates route requests with ranking logic.
- `ranking_engine/`: Recommendation algorithms, scoring rules, and ranking utilities.
- `models/`: SQLAlchemy ORM models for users, items, and interactions.
- `schemas/`: Pydantic request and response schemas.
- `core/`: Shared constants and application-level configuration values.
- `db.py`: SQLAlchemy engine, session factory, and database dependency.
- `main.py`: FastAPI application setup and router registration.

## Recommendation Engine

RecoCore uses deterministic ranking logic rather than machine learning. This keeps the system explainable, easy to test, and suitable for backend-focused recommendation workflows.

### 1. Trending Recommendations

Trending recommendations aggregate interaction weights by item, then rank items by the resulting score.

Supported interaction weights:

```text
view     -> 1
like     -> 3
share    -> 5
purchase -> 8
```

Trending flow:

```text
Interactions
    |
    v
Group by item_id
    |
    v
Sum interaction weights
    |
    v
Sort by score descending
    |
    v
Return top N items
```

Trending recommendations can also be filtered by category:

```text
GET /recommendations/trending?category=gaming&limit=10
```

### 2. Decay Scoring

Decay scoring reduces the impact of older interactions while still allowing them to contribute. The multiplier bottoms out at `0.2`, so older interactions never become completely irrelevant.

Decay flow:

```text
Interaction date
    |
    v
Calculate age in days
    |
    v
Apply decay multiplier
    |
    v
effective_weight = interaction_weight * decay_multiplier
```

### 3. Category Affinity

Category affinity analyzes a user's historical interactions and calculates preference scores per category using decay-adjusted weights.

Category affinity flow:

```text
User interactions
    |
    v
Join interactions with items
    |
    v
Read item category + interaction weight + interaction age
    |
    v
Apply decay scoring
    |
    v
Aggregate score by category
    |
    v
Determine primary and secondary categories
```

### 4. Personalized Recommendations

Personalized recommendations use category affinity to build a balanced result set.

Rules:

- Calculate category affinity for the user.
- Determine primary and secondary categories.
- Exclude items the user has liked, shared, or purchased.
- Keep viewed items eligible.
- Generate recommendations using:
  - 70% primary category
  - 20% secondary category
  - 10% trending items

Personalized recommendation flow:

```text
Request user recommendations
    |
    v
Calculate category affinity
    |
    v
Find primary and secondary categories
    |
    v
Fetch excluded item IDs
    |
    v
Get 70% primary category items
    |
    v
Get 20% secondary category items
    |
    v
Get 10% trending fallback items
    |
    v
Merge and limit results
```

### 5. Cold Start Handling

For users without enough interaction history, the engine can fall back to trending recommendations so the API still returns useful items.

Cold-start flow:

```text
User has no interaction history
    |
    v
No category affinity available
    |
    v
Use trending recommendation strategy
    |
    v
Return popular items
```

## API Endpoints

### Health Check

```http
GET /
```

Example response:

```json
{
  "success": true,
  "message": "RecoCore API is running"
}
```

### Create Interaction

```http
POST /interactions
```

Request body:

```json
{
  "user_id": 1,
  "item_id": 10,
  "action_type": "like"
}
```

Supported `action_type` values:

```text
view
like
share
purchase
```

Example response:

```json
{
  "success": true,
  "message": "Interaction created successfully",
  "data": {
    "interaction_id": 101,
    "user_id": 1,
    "item_id": 10,
    "action_type": "like",
    "weight": 3.0,
    "created_at": "2026-06-19T13:00:00"
  }
}
```

### Trending Recommendations

```http
GET /recommendations/trending?limit=10
```

With category filter:

```http
GET /recommendations/trending?limit=10&category=gaming
```

Example response:

```json
{
  "success": true,
  "message": "Trending recommendations fetched successfully",
  "data": [
    {
      "item_id": 80,
      "name": "Public-key heuristic matrices",
      "category": "gaming",
      "score": 24
    }
  ]
}
```

### Personalized Recommendations

```http
GET /recommendations/users/1?limit=10
```

Example response:

```json
[
  {
    "item_id": 1,
    "name": "Synergistic fault-tolerant superstructure",
    "category": "electronics"
  },
  {
    "item_id": 8,
    "name": "Reduced impactful focus group",
    "category": "books"
  }
]
```

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd recocore
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
POSTGRES_DB=recocore
POSTGRES_USER=recocore
POSTGRES_PASSWORD=recocore
POSTGRES_PORT=5432
DATABASE_URL=postgresql+psycopg2://recocore:recocore@postgres:5432/recocore
```

If running the API locally outside Docker, use a database host reachable from your machine, for example:

```env
DATABASE_URL=postgresql+psycopg2://recocore:recocore@localhost:5432/recocore
```

## Docker Setup

Start the API and PostgreSQL with Docker Compose:

```bash
docker compose up --build
```

The API runs at:

```text
http://localhost:8000
```

Interactive API docs are available at:

```text
http://localhost:8000/docs
```

Stop the containers:

```bash
docker compose down
```

Stop the containers and remove the PostgreSQL volume:

```bash
docker compose down -v
```

## Seeding Data

The project includes a seed script for creating sample users, items, and interactions.

Run it from the project root:

```bash
python -m scripts.seed_data
```

The script clears and repopulates the seed tables.

## Testing

Run the test suite:

```bash
pytest -q
```

Run specific test files:

```bash
pytest -q tests/test_interaction.py
pytest -q tests/test_recommendation.py
```

Current pytest coverage includes:

- Interaction creation through the API.
- Missing-user handling for interaction creation.
- Trending recommendation category filtering.
- Personalized recommendation count validation.
- Duplicate recommendation prevention.
- Exclusion logic for liked, shared, and purchased items.
- Personalized recommendation category distribution for the 70/20/10 strategy.
- Cold-start behavior through trending fallback strategy.

## Project Structure

```text
.
├── app/
│   ├── core/
│   │   ├── __init__.py
│   │   └── constants.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── interaction_model.py
│   │   ├── item_model.py
│   │   └── user_model.py
│   ├── ranking_engine/
│   │   ├── __init__.py
│   │   ├── personalised.py
│   │   ├── scoring.py
│   │   ├── similarity.py
│   │   └── trending.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── interaction_routes.py
│   │   └── recommendation_routes.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── common_schema.py
│   │   ├── interaction_schema.py
│   │   └── recommendation_schema.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── interaction_service.py
│   │   └── recommendation_service.py
│   ├── config.py
│   ├── db.py
│   └── main.py
├── scripts/
│   └── seed_data.py
├── tests/
│   ├── test_interaction.py
│   └── test_recommendation.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## Future Improvements

- Add database migrations with Alembic.
- Add pagination metadata for recommendation endpoints.
- Add endpoint-level tests for cold-start users.
- Add more ranking strategies for similarity and diversity.
- Add request logging and structured application logs.
- Add CI workflow for linting and pytest.
- Add production deployment configuration.

## Summary

RecoCore is a backend-focused recommendation engine API that demonstrates practical service architecture, SQLAlchemy-based persistence, deterministic ranking algorithms, and testable recommendation behavior. It is designed to be readable, extensible, and suitable for showcasing backend engineering skills.
