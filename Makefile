build:
	docker-compose build

up:
	docker-compose up -d

test:
	docker-compose exec backend pytest