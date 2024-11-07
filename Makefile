
test:
	pytest --cov=app --cov-report=term --cov-report=html

lint:
	pylint .  --fail-under=10

format:
	black .

perfect: format lint test
