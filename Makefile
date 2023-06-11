build:
	docker-compose build

up:
	docker-compose up -d

test:
	docker-compose exec backend pytest # а у меня и так находит тесты