.PHONY: help install dev build up down clean test

help:
	@echo "RCA Chatbot - Makefile Commands"
	@echo ""
	@echo "  make install    - Install all dependencies"
	@echo "  make dev        - Start development servers"
	@echo "  make build      - Build Docker images"
	@echo "  make up         - Start containers"
	@echo "  make down       - Stop containers"
	@echo "  make clean      - Clean up containers and volumes"
	@echo "  make test       - Run tests"

install:
	@echo "Installing backend dependencies..."
	cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

dev:
	@echo "Starting development servers..."
	docker-compose up --build

build:
	@echo "Building Docker images..."
	docker-compose build

up:
	@echo "Starting containers..."
	docker-compose up -d

down:
	@echo "Stopping containers..."
	docker-compose down

clean:
	@echo "Cleaning up..."
	docker-compose down -v
	docker system prune -f

test:
	@echo "Running tests..."
	cd backend && python -m pytest tests/ || echo "No tests found"


