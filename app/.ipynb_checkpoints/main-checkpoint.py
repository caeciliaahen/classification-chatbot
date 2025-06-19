from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router_diagnosis  # pastikan path sesuai struktur direktori

app = FastAPI(
    title="API Diagnosis Penyakit Hewan",
    description="Backend API untuk mendiagnosis penyakit hewan berdasarkan input gejala",
    version="1.0"
)

# === Middleware CORS (agar bisa diakses dari frontend) ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ganti dengan domain frontend yang fix
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Include Routing Diagnosis ===
app.include_router(router_diagnosis.router)

# Optional: Root check
@app.get("/")
def root():
    return {"message": "Halo! API Diagnosis Penyakit Hewan aktif."}