# Flask Backend API (Manufacturing Defect Management System)

Implements the REST API described by `tmp_backend_openapi.json`:
- Auth: `/api/auth/signup`, `/api/auth/login`
- Defects CRUD + RCA: `/api/defects`, `/api/defects/{id}`, `/api/defects/{id}/rca`
- Corrective actions: `/api/actions`, `/api/actions/{id}`
- Overdue dashboard: `/api/dashboard/overdue-actions`
- Analytics: `/api/analytics/pareto`, `/api/analytics/trends`
- Uploads: `POST /api/uploads` and public serving `GET /uploads/{file_id}`
- PDF export: `GET /api/defects/{id}/export`

## Environment
See `.env.example` (do not commit real secrets).

## Run (dev)
```bash
pip install -r requirements.txt
python main.py
```
