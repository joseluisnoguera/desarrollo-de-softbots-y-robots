build:
	docker-compose build

up:
	docker-compose up --build

down:
	docker-compose down

logs:
	docker-compose logs -f

lint:
	ruff check . --fix

local:
	streamlit run Home.py --server.port=8501 --server.address=0.0.0.0