# Belenergy Ventas — comandos de desarrollo con Docker Compose (Mac/Windows/Linux).
#
# Requiere: Docker Desktop (Mac/Windows) o Docker Engine (Linux) + docker compose v2.
# Uso: make up  |  make down  |  make logs  ...
#
# Nota: esto es UNA VIA de correr el proyecto. Railway despliega desde el root
# Dockerfile con variables del dashboard; nada de esto afecta el deploy.

SHELL := /bin/sh

COMPOSE := docker compose
SERVICES := api db

.PHONY: up down ps logs rebuild reset build help

## up — construye (si hubo cambios) y levanta Postgres + API (frontend web incluido). Primer run: build largo.
up:
	$(COMPOSE) up -d --build
	@echo ""
	@echo "App lista en http://localhost:$${API_PORT:-8000}  (login por defecto: admin / admin123)"
	@echo "Health:  curl http://localhost:$${API_PORT:-8000}/health"

## down — detiene (sin borrar datos de Postgres).
down:
	$(COMPOSE) down

## ps — estado de los contenedores.
ps:
	$(COMPOSE) ps

## logs — tail en vivo de todos los servicios (Ctrl+C para salir).
logs:
	$(COMPOSE) logs -f --tail=100

## rebuild — borra y reconstruye imagenes y levanta del volumen de datos (sin borrarlo).
rebuild: down
	$(COMPOSE) build --no-cache
	$(COMPOSE) up -d

## reset — detiene, borra contenedores E imagenes y ELIMINA el volumen de datos (pgdata).
reset: down
	$(COMPOSE) rm -f
	$(COMPOSE) down -v

## build — solo construye las imagenes (sin levantar).
build:
	$(COMPOSE) build

## help — lista los comandos disponibles.
help:
	@echo "Comandos disponibles: up, down, ps, logs, rebuild, reset, build, help"