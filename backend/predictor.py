import re
from typing import Dict, Any, List, Optional

DEFAULT_WEIGHTS = {
    "odds": 0.30,
    "musique": 0.20,
    "deferre": 0.15,
    "driver": 0.15,
    "oeilleres": 0.10,
    "earnings": 0.05,
    "age": 0.05
}

def parse_musique_score(musique: str) -> float:
    if not musique or not isinstance(musique, str):
        return 50.0

    tokens = re.findall(r'(\d+|D|A|0)([a-zA-Z])', musique)
    if not tokens:
        return 50.0

    scores = []
    weights = [1.0, 0.85, 0.7, 0.55, 0.4]

    for idx, (pos_str, disc) in enumerate(tokens[:5]):
        weight = weights[idx] if idx < len(weights) else 0.3
        if pos_str in ('D', 'A', '0'):
            score = 15.0
        else:
            try:
                pos = int(pos_str)
                if pos == 1:
                    score = 100.0
                elif pos == 2:
                    score = 85.0
                elif pos == 3:
                    score = 70.0
                elif pos <= 5:
                    score = 50.0
                elif pos <= 9:
                    score = 30.0
                else:
                    score = 15.0
            except ValueError:
                score = 30.0
        scores.append(score * weight)

    if not scores:
        return 50.0

    total_weight = sum(weights[:len(scores)])
    return round(sum(scores) / total_weight, 1)


def calculate_odds_probability(cote: Any) -> float:
    if not cote or not isinstance(cote, (int, float)) or float(cote) <= 1.0:
        return 5.0
    implied_prob = (1.0 / float(cote)) * 100.0
    return min(implied_prob, 85.0)


def calculate_deferrage_bonus(deferre: Optional[str], discipline: str) -> float:
    if not deferre or not isinstance(deferre, str):
        return 50.0

    d = deferre.upper()
    if "ANTERIEURS_POSTERIEURS" in d or "D4" in d:
        return 95.0
    elif "ANTERIEURS" in d or "POSTERIEURS" in d or "DP" in d or "DA" in d:
        return 75.0
    elif "PROTEGE" in d:
        return 60.0
    return 40.0


def calculate_oeilleres_bonus(oeilleres: Optional[str]) -> float:
    if not oeilleres or not isinstance(oeilleres, str):
        return 50.0
    o = oeilleres.upper()
    if "OEILLERES_CLASSIQUE" in o or "AVEC_OEILLERES" in o:
        return 80.0
    elif "OEILLERES_AUSTRALIENNES" in o:
        return 75.0
    return 50.0


def calculate_driver_trainer_bonus(driver: str, trainer: str) -> float:
    top_drivers = ["E. RAFFIN", "M. ABRIVARD", "F. NIVARD", "J.M. BAZIRE", "A. ABRIVARD", "G. GELORMINI", "M. MOTTIER", "M. GUYON", "C. SOUMILLON", "S. PASQUIER", "M. BARZALONA", "A. MADAMET"]
    top_trainers = ["J.M. BAZIRE", "T. MALMQVIST", "S. GUARATO", "P. ALLAIRE", "A. CHAVATTE", "F. LEBLANC", "A. FABRE", "JC. ROUGET", "C. FERLAND"]

    bonus = 50.0
    if driver and any(td in driver.upper() for td in top_drivers):
        bonus += 25.0
    if trainer and any(tt in trainer.upper() for tt in top_trainers):
        bonus += 25.0
    return min(bonus, 100.0)


def calculate_runner_prediction(
    runner: Dict[str, Any],
    race_info: Dict[str, Any],
    total_runners: int,
    custom_weights: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    weights = DEFAULT_WEIGHTS.copy()
    if custom_weights:
        weights.update(custom_weights)

    odds = runner.get("cote")
    odds_prob = calculate_odds_probability(odds)
    musique_score = parse_musique_score(runner.get("musique", ""))
    deferre_score = calculate_deferrage_bonus(runner.get("deferre"), race_info.get("discipline", ""))
    oeilleres_score = calculate_oeilleres_bonus(runner.get("oeilleres"))
    driver_trainer_score = calculate_driver_trainer_bonus(runner.get("driver", ""), runner.get("entraineur", ""))

    gains = runner.get("gain", 0) or 0
    earnings_score = min(50.0 + (gains / 2000.0), 100.0)

    age = runner.get("age", 5) or 5
    age_score = 90.0 if 4 <= age <= 7 else 70.0

    weighted_score = (
        (odds_prob * weights.get("odds", 0.30)) +
        (musique_score * weights.get("musique", 0.20)) +
        (deferre_score * weights.get("deferre", 0.15)) +
        (driver_trainer_score * weights.get("driver", 0.15)) +
        (oeilleres_score * weights.get("oeilleres", 0.10)) +
        (earnings_score * weights.get("earnings", 0.05)) +
        (age_score * weights.get("age", 0.05))
    )

    num_val = runner.get("num") or runner.get("numPmu") or runner.get("numOrdre")

    return {
        "num": num_val,
        "nom": runner.get("nom"),
        "age": age,
        "sexe": runner.get("sexe"),
        "musique": runner.get("musique"),
        "driver": runner.get("driver"),
        "entraineur": runner.get("entraineur"),
        "cote": odds,
        "deferre": runner.get("deferre"),
        "oeilleres": runner.get("oeilleres"),
        "speed_str": runner.get("speed_str"),
        "raw_score": round(weighted_score, 1),
        "musique_score": musique_score,
        "deferre_score": deferre_score,
        "driver_trainer_score": driver_trainer_score
    }


def predict_race_outcomes(
    parsed_race_data: Dict[str, Any],
    custom_weights: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    runners = parsed_race_data.get("participants", [])
    if not runners:
        return {**parsed_race_data, "ranked_runners": [], "confidence": "FAIBLE"}

    total_runners = len(runners)
    predictions = [calculate_runner_prediction(r, parsed_race_data, total_runners, custom_weights) for r in runners]

    total_raw_score = sum(p["raw_score"] for p in predictions) or 1.0

    for p in predictions:
        win_prob = (p["raw_score"] / total_raw_score) * 100.0
        p["prob_victoire"] = round(win_prob, 1)
        p["prob_place"] = round(min(win_prob * 2.2 + 12.0, 95.0), 1)

        cote = p.get("cote")
        market_prob = calculate_odds_probability(cote) if cote else 100.0

        value_ratio = (win_prob / market_prob) if market_prob > 0 else 0
        p["value_ratio"] = round(value_ratio, 2)

        # Minimum odds and market stability checks for Value Bets
        min_odds_threshold = 3.0
        max_odds_cap = 80.0  # Guard against hyper-volatile longshots on low-volume markets
        is_stable_market = bool(total_runners >= 4)  # Guard for low-volume races with < 4 runners

        is_vb = bool(
            cote and
            float(cote) >= min_odds_threshold and
            float(cote) <= max_odds_cap and
            value_ratio >= 1.25 and
            is_stable_market
        )
        p["is_value_bet"] = is_vb

        if cote and float(cote) > 1.0 and p["is_value_bet"]:
            b = float(cote) - 1.0
            p_win = win_prob / 100.0
            q_loss = 1.0 - p_win
            kelly_f = (p_win * b - q_loss) / b
            suggested_stake_pct = min(max(round((kelly_f * 0.25) * 100.0, 1), 1.0), 5.0)
            p["kelly_stake_pct"] = suggested_stake_pct
        else:
            p["kelly_stake_pct"] = 0.0

    ranked_runners = sorted(predictions, key=lambda x: x["raw_score"], reverse=True)

    for rank, runner in enumerate(ranked_runners, 1):
        runner["predicted_rank"] = rank

    top1_prob = ranked_runners[0]["prob_victoire"] if len(ranked_runners) > 0 else 0
    top2_prob = ranked_runners[1]["prob_victoire"] if len(ranked_runners) > 1 else 0
    gap = top1_prob - top2_prob

    if gap > 12.0:
        confidence = "TRES_ELEVE"
    elif gap > 6.0:
        confidence = "ELEVE"
    elif gap > 3.0:
        confidence = "MOYEN"
    else:
        confidence = "FAIBLE"

    return {
        **parsed_race_data,
        "ranked_runners": ranked_runners,
        "confidence": confidence,
        "active_weights": custom_weights or DEFAULT_WEIGHTS
    }
