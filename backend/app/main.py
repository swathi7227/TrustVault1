
from fastapi import FastAPI

from backend.app.auth.routes import router as auth_router
from backend.app.documents.routes import router as documents_router

app = FastAPI(
    title="TrustVault API",
    description="Secure document management with server-side authorization",
    version="1.0.0",
)

app.include_router(auth_router)
app.include_router(documents_router)


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}
