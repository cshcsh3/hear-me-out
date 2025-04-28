# Hear Me Out

A simple audio transcribing webapp

## Running it via Docker
To start the app via docker
```bash
docker compose up frontend backend
```

### Tests
Tests can be run via docker as well without any pre-requisites
```bash
docker compose up backend-test
docker compose up frontend-test
```

## Running it locally

Pre-requisites:
- Python 3.13
- Node.js 22
- npm
- pip

### Backend
Ensure virtual environment is created and depedencies are installed

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install .[dev]
```

#### Tests
```bash
pytest
```

#### Local dev
```bash
uvicorn src.main:app --reload --port 3001
```

### Frontend 
Ensure dependencies are installed
```bash
cd frontend
npm install
```

#### Tests
```bash
npm test
```

#### Local dev
```bash
npm start
```