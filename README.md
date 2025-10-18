# Impact Analyzer FastAPI

A simple FastAPI application with basic endpoints. {to be edited}

## Setup

1. Create a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
uvicorn main:app --reload
```

4. Open your browser to `http://localhost:8000` or visit `http://localhost:8000/docs` for the interactive API documentation.

## Endpoints

- `GET /` - Returns a simple "Hello World!" message
- `GET /health` - Health check endpoint
- `GET /hello/{name}` - Personalized greeting

## Example Usage

```bash
# Basic hello
curl http://localhost:8000/

# Health check
curl http://localhost:8000/health

# Personalized greeting
curl http://localhost:8000/hello/John
```
