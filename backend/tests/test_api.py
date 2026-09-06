import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.predictor import parse_musique_score, calculate_odds_probability, predict_race_outcomes, calculate_deferrage_bonus, calculate_oeilleres_bonus
from backend.pmu_bets import generate_pmu_bet_recommendations
from backend.backtest import generate_mock_backtest_data, evaluate_prediction_performance

client = TestClient(app)

def test_healthcheck():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_parse_musique_score():
    score_1st = parse_musique_score("1a2a3a")
    score_unplaced = parse_musique_score("0aDa9a")
    assert score_1st > score_unplaced

def test_deferrage_and_equipment_bonuses():
    assert calculate_deferrage_bonus("DEFERRE_ANTERIEURS_POSTERIEURS", "ATTELE") > calculate_deferrage_bonus(None, "ATTELE")
    assert calculate_oeilleres_bonus("OEILLERES_CLASSIQUE") > calculate_oeilleres_bonus(None)

def test_predict_race_outcomes_with_custom_weights():
    mock_race = {
        "date": "05092025",
        "reunion": 1,
        "course": 1,
        "libelle": "Prix Test Custom Weights",
        "discipline": "ATTELE",
        "distance": 2100,
        "hippodrome": "Vincennes",
        "participants": [
            {"numPmu": 1, "nom": "Cheval Un", "age": 5, "musique": "0a0a0a", "cote": 1.2},
            {"numPmu": 2, "nom": "Cheval Deux", "age": 6, "musique": "1a1a1a", "cote": 20.0},
        ]
    }

    # Heavy odds weight -> Cheval Un first
    pred_odds = predict_race_outcomes(mock_race, custom_weights={"odds": 0.90, "musique": 0.05})
    assert pred_odds["ranked_runners"][0]["num"] == 1

    # Heavy musique weight -> Cheval Deux first
    pred_musique = predict_race_outcomes(mock_race, custom_weights={"odds": 0.05, "musique": 0.90})
    assert pred_musique["ranked_runners"][0]["num"] == 2

def test_non_runner_filtering_in_bets():
    predicted_data = {
        "ranked_runners": [
            {"num": 1, "nom": "Cheval NP", "non_partant": True, "cote": 2.0},
            {"num": 2, "nom": "Cheval Valide 1", "cote": 3.0, "prob_place": 80.0},
            {"num": 3, "nom": "Cheval Valide 2", "cote": 5.0, "prob_place": 60.0},
            {"num": 4, "nom": "Cheval Valide 3", "cote": 8.0, "prob_place": 40.0},
        ]
    }

    bets = generate_pmu_bet_recommendations(predicted_data)
    assert "simple_gagnant" in bets
    # Favori must NOT be Cheval NP (num 1)
    assert "N°1" not in bets["simple_gagnant"]["favori"]
    assert "N°2" in bets["simple_gagnant"]["favori"]

def test_backtest_evaluation_module():
    mock_history = generate_mock_backtest_data(num_races=20)
    assert len(mock_history) == 20

    metrics = evaluate_prediction_performance(mock_history)
    assert metrics["total_races"] == 20
    assert "roi_pct" in metrics
    assert "win_rate_pct" in metrics

def test_endpoints():
    res_today = client.get("/api/races/today")
    assert res_today.status_code == 200

    res_summary = client.get("/api/summary/today")
    assert res_summary.status_code == 200

    res_backtest = client.get("/api/backtest?days=30")
    assert res_backtest.status_code == 200
    json_data = res_backtest.json()
    assert "metrics" in json_data
    assert json_data["metrics"]["total_races"] == 30
    assert "roi_pct" in json_data["metrics"]
