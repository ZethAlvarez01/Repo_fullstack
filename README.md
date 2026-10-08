# Mi Proyecto

Monorepo con una interfaz Vue 3/Vite y una API FastAPI conectada a MongoDB.

## Estructura

```text
mi-proyecto/
├── frontend/       # Aplicacion Vue + Vite
├── backend/        # API FastAPI
├── .gitignore
└── README.md
```

## Requisitos

- Node.js 20 o superior
- Python 3.10 o superior
- Una base de datos MongoDB

## Frontend

```bash
cd frontend
npm install
npm run dev
```

La aplicacion queda disponible en la URL que muestre Vite (normalmente `http://localhost:5173`). Para generar la version de produccion usa `npm run build`.

## Backend

Desde la raiz del repositorio:

```bash
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

Completa `backend/.env` con los datos reales de MongoDB. El archivo contiene secretos y esta excluido de Git. La API se ejecuta normalmente en `http://localhost:8000`; puedes revisar su estado en `GET /health` y la documentacion interactiva en `/docs`.

## Subir a GitHub

```bash
git init
git add .
git commit -m "Initial monorepo structure"
```

Antes de publicar, confirma que `backend/.env`, `backend/.venv/` y `frontend/node_modules/` no aparezcan en `git status`.
