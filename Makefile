.PHONY: install train test docker-build k8s-apply clean

install:
	pip install -r requirements.txt

train:
	python src/api/train.py --data-path data/bank-additional-full.csv

train-synthetic:
	python src/api/train.py

test:
	pytest tests/ -v --cov=src --cov-report=term-missing

docker-build:
	docker build -t mlops-k8s-platform:latest .

docker-run:
	docker run -p 8000:8000 mlops-k8s-platform:latest

k8s-apply:
	kubectl apply -f k8s/base/namespace.yaml
	kubectl apply -f k8s/base/deployment.yaml
	kubectl apply -f k8s/base/service.yaml
	kubectl apply -f k8s/base/hpa.yaml

k8s-status:
	kubectl get all -n mlops

clean:
	rm -rf artifacts/ __pycache__
	find . -name "*.pyc" -delete
