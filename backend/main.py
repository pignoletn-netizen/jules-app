from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import Base, engine
from backend.routers import (
    auth_router,
    products_router,
    suppliers_router,
    landing_router,
    compliance_router,
    marketing_router,
    sav_router,
    financials_router,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MVB Platform API",
    description="API complète pour la gestion, le sourcing, la validation de marché, le marketing et l'automatisation d'un business MVB.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(products_router.router)
app.include_router(suppliers_router.router)
app.include_router(landing_router.router)
app.include_router(compliance_router.router)
app.include_router(marketing_router.router)
app.include_router(sav_router.router)
app.include_router(financials_router.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "app": "MVB Platform Backend"}
