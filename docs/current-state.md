# Current State of Belenergy-Ventas

This document outlines the current functional state of the Belenergy-Ventas repository.

## Backend
- **Framework:** FastAPI (Python)
- **Database:** Uses SQLAlchemy ORM.
- **Health Check:** Provides a basic `/health` endpoint.
- **Functionality:** Primarily serves authentication purposes at this stage.

## Frontend
- **Framework:** Flutter (Web-capable)
- **Features:** 
    - Login Screen: Includes email/password fields, validation, error handling via `AuthProvider`, and visual feedback (loading indicators, error messages).
    - Navigation: Basic routing setup with a splash screen, login screen, and home screen.
    - Assets: Includes branded assets (Belenergy ARG logo).

## Authentication
- **Backend:** 
    - Endpoints: `/auth/register` (POST), `/auth/login` (POST), `/auth/me` (GET, protected).
    - Logic: Implements password hashing and JWT-based authentication with expiration.
- **Frontend:** 
    - Manages authentication state via `AuthProvider`.
    - Handles user login flow and persistent session management logic.

## Infrastructure
- **Containerization:** Dockerfile present in `Backend` directory and `docker-compose.yml` at the root, facilitating containerized deployment.
