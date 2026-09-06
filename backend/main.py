from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any

from backend.pmu_api import get_daily_programme, get_parsed_race_data, format_date
from backend.predictor import predict_race_outcomes
from backend.pmu_bets import generate_pmu_bet_recommendations
from backend.backtest import generate_mock_backtest_data, evaluate_prediction_performance

app = FastAPI(
    title="Turf Predictor & PMU Bet Advisor API",
    description="API de pronostics hippiques multi-critères et récapitulatif de mises PMU.fr",
    version="1.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def healthcheck():
    return {"status": "ok", "service": "Turf Predictor API", "version": "1.2.0"}

@app.get("/api/races/today")
def get_races_today(date: Optional[str] = Query(None, description="Date au format YYYY-MM-DD ou DDMMYYYY")):
    date_formatted = format_date(date)
    programme = get_daily_programme(date_formatted)

    if not programme or "programme" not in programme:
        return {"date": date_formatted, "reunions": []}

    reunions_raw = programme.get("programme", {}).get("reunions", [])
    reunions_list = []

    for r in reunions_raw:
        num_r = r.get("numOfficiel", r.get("numOrdre"))
        hippo = r.get("hippodrome", {})
        hippo_name = hippo.get("libelleCourt") or hippo.get("libelleLong") or f"Hippodrome R{num_r}" if isinstance(hippo, dict) else f"Hippodrome R{num_r}"

        courses_raw = r.get("courses", [])
        courses_list = []

        for c in courses_raw:
            num_c = c.get("numOrdre", c.get("numExterne"))
            courses_list.append({
                "num": num_c,
                "reunion": num_r,
                "libelle": c.get("libelle"),
                "discipline": c.get("discipline"),
                "distance": c.get("distance"),
                "heureDepart": c.get("heureDepart"),
                "nombrePartants": c.get("nombreDeclaresPartants")
            })

        reunions_list.append({
            "num": num_r,
            "hippodrome": hippo_name,
            "pays": r.get("pays", {}).get("libelle") if isinstance(r.get("pays"), dict) else "FRANCE",
            "disciplines": r.get("disciplinesMeres", []),
            "courses": courses_list
        })

    return {
        "date": date_formatted,
        "reunions": reunions_list
    }

@app.get("/api/races/{date}/{reunion}/{course}")
def get_race_analysis(date: str, reunion: int, course: int):
    raw_data = get_parsed_race_data(date_str=date, num_reunion=reunion, num_course=course)
    if not raw_data.get("participants"):
        raise HTTPException(status_code=404, detail="Course non trouvée ou aucun partant disponible")

    predicted = predict_race_outcomes(raw_data)
    bets = generate_pmu_bet_recommendations(predicted)

    return {
        "race_info": {
            "date": predicted["date"],
            "reunion": predicted["reunion"],
            "course": predicted["course"],
            "libelle": predicted["libelle"],
            "discipline": predicted["discipline"],
            "distance": predicted["distance"],
            "hippodrome": predicted["hippodrome"],
            "terrain": predicted["terrain"],
            "corde": predicted["corde"],
            "conditions": predicted["conditions"],
            "nombrePartants": predicted["nombreDeclaresPartants"],
            "confidence": predicted["confidence"]
        },
        "ranked_runners": predicted["ranked_runners"],
        "pmu_bets": bets
    }

@app.get("/api/summary/today")
def get_daily_pmu_summary(date: Optional[str] = Query(None)):
    date_formatted = format_date(date)
    programme = get_daily_programme(date_formatted)

    if not programme or "programme" not in programme:
        return {"date": date_formatted, "summary": []}

    reunions_raw = programme.get("programme", {}).get("reunions", [])
    summary_list = []

    for r in reunions_raw[:4]:
        num_r = r.get("numOfficiel", r.get("numOrdre"))
        hippo = r.get("hippodrome", {})
        hippo_name = hippo.get("libelleCourt") or hippo.get("libelleLong") or f"Hippodrome R{num_r}" if isinstance(hippo, dict) else f"Hippodrome R{num_r}"

        courses_raw = r.get("courses", [])
        for c in courses_raw:
            num_c = c.get("numOrdre", c.get("numExterne"))
            try:
                raw_data = get_parsed_race_data(date_str=date_formatted, num_reunion=num_r, num_course=num_c)
                if raw_data.get("participants"):
                    predicted = predict_race_outcomes(raw_data)
                    bets = generate_pmu_bet_recommendations(predicted)

                    value_runners = [runner for runner in predicted.get("ranked_runners", []) if runner.get("is_value_bet")]

                    summary_list.append({
                        "reunion": num_r,
                        "course": num_c,
                        "hippodrome": hippo_name,
                        "libelle": c.get("libelle"),
                        "discipline": c.get("discipline"),
                        "distance": c.get("distance"),
                        "confidence": predicted.get("confidence"),
                        "top_runners": [
                            {
                                "num": r["num"],
                                "nom": r["nom"],
                                "prob_victoire": r["prob_victoire"],
                                "cote": r["cote"],
                                "is_value_bet": r.get("is_value_bet", False),
                                "kelly_stake_pct": r.get("kelly_stake_pct", 0.0)
                            }
                            for r in predicted.get("ranked_runners", [])[:3]
                        ],
                        "has_value_bets": len(value_runners) > 0,
                        "bets_preview": {
                            "simple_favori": bets.get("simple_gagnant", {}).get("favori"),
                            "simple_outsider": bets.get("simple_gagnant", {}).get("value_bet"),
                            "trio_base": bets.get("trio", {}).get("base"),
                            "quinte_base": bets.get("quinte", {}).get("base_quinte"),
                            "multi_4": bets.get("multi", {}).get("multi_en_4")
                        }
                    })
            except Exception:
                continue

    return {
        "date": date_formatted,
        "summary": summary_list
    }

@app.get("/api/backtest")
def get_backtest_results(
    days: int = Query(30, ge=1, le=180, description="Nombre de jours de backtest (1 à 180)")
):
    history = generate_mock_backtest_data(num_races=days)
    metrics = evaluate_prediction_performance(history)
    return {
        "period_days": days,
        "metrics": metrics,
        "recent_history": history[:20]
    }
