import os
import shutil
from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.services.species_service import search_species_data
from backend.services.analysis_service import run_inventory_analysis

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
SAMPLE_EXCEL_PATH = os.path.join(DATA_DIR, "sample_inventory.xlsx")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

app = FastAPI(
    title="Spider Ecology & Inventory Analysis API",
    description="API for spider species lookup (INPN/Taxref) and Excel inventory statistical analysis with R",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount output directory for plot images
app.mount("/static/output", StaticFiles(directory=OUTPUT_DIR), name="output_static")


@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "Backend service is running."}


@app.get("/api/species/search")
def search_species(name: str = Query(..., min_length=2, description="Spider species scientific name")):
    try:
        data = search_species_data(name)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Species lookup error: {str(e)}")


@app.post("/api/analysis/upload")
async def upload_and_analyze(file: UploadFile = File(...)):
    if not (file.filename.endswith(".xlsx") or file.filename.endswith(".xls")):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload an Excel file (.xls or .xlsx).")

    upload_path = os.path.join(DATA_DIR, f"uploaded_{file.filename}")
    try:
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        results = run_inventory_analysis(upload_path)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/api/analysis/sample")
def get_sample_inventory():
    if not os.path.exists(SAMPLE_EXCEL_PATH):
        # Generate sample inventory if not existing
        import pandas as pd
        import numpy as np
        import datetime

        np.random.seed(42)
        species = [
            ('Agelena labyrinthica', 'Agelenidae'),
            ('Textrix denticulata', 'Agelenidae'),
            ('Pardosa amentata', 'Lycosidae'),
            ('Pardosa lugubris', 'Lycosidae'),
            ('Alopecosa pulverulenta', 'Lycosidae'),
            ('Xysticus cristatus', 'Thomisidae'),
            ('Ozyptila atomaria', 'Thomisidae'),
            ('Clubiona reclusa', 'Clubionidae'),
            ('Salticus scenicus', 'Salticidae'),
            ('Araneus diadematus', 'Araneidae')
        ]
        stations = ['Prairie_A', 'Foret_B', 'Zone_Humide_C', 'Lisiere_D']
        rows = []
        base_date = datetime.date(2023, 5, 1)

        for i in range(80):
            sp, fam = species[np.random.choice(len(species))]
            st = np.random.choice(stations)
            mc = np.random.choice(['barber', 'barber', 'barber', 'fauchage', 'battage'])
            date = base_date + datetime.timedelta(days=int(np.random.randint(0, 30)))
            trap_id = f'P_{st}_{np.random.randint(1, 4)}'
            males = int(np.random.randint(0, 5))
            females = int(np.random.randint(0, 5))
            juvs = int(np.random.randint(0, 10))
            ad = males + females
            tot_ab = ad + juvs
            if tot_ab > 0:
                rows.append({
                    'Genresp': sp,
                    'Famille': fam,
                    'Date': date.strftime('%Y-%m-%d'),
                    'Capture': trap_id,
                    'Mâles': males,
                    'Fem': females,
                    'Juv': juvs,
                    'Ad': ad,
                    'Tot ab': tot_ab,
                    'Station': st,
                    'ModeCapt': mc
                })

        df = pd.DataFrame(rows)
        df.to_excel(SAMPLE_EXCEL_PATH, index=False)

    return FileResponse(
        SAMPLE_EXCEL_PATH,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="modele_inventaire_araignees.xlsx"
    )


@app.get("/api/analysis/download/{filename}")
def download_file(filename: str):
    file_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    media_type = "application/octet-stream"
    if filename.endswith(".xlsx"):
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif filename.endswith(".png"):
        media_type = "image/png"

    return FileResponse(file_path, media_type=media_type, filename=filename)
