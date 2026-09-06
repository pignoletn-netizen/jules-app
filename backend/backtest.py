"""
Backtesting and ROI Performance Evaluation Module for PMU Turf Predictions.
Calculates win rates, ROI %, profit/loss, and yield on historical predictions.
"""

from typing import List, Dict, Any, Optional


def evaluate_prediction_performance(
    history_records: List[Dict[str, Any]],
    flat_stake: float = 10.0,
    strategy: str = "ALL"
) -> Dict[str, Any]:
    """
    Evaluates historical predictions against race outcomes.

    Each record in history_records should contain:
      - race_id: str
      - date: str
      - predictions: List[Dict] with 'num', 'prob_victoire', 'is_value_bet', 'kelly_stake_pct'
      - actual_results: List[int] ordered by finish place [1st_num, 2nd_num, 3rd_num, 4th_num, 5th_num]
      - actual_odds: Dict[int, float] mapping runner 'num' to final payout odds

    Returns ROI, Win Rate, total staked, total payout, and performance breakdown.
    """
    total_races = len(history_records)
    if total_races == 0:
        return {
            "total_races": 0,
            "total_staked": 0.0,
            "total_payout": 0.0,
            "net_profit": 0.0,
            "roi_pct": 0.0,
            "win_rate_pct": 0.0,
            "placed_rate_pct": 0.0,
            "value_bet_roi_pct": 0.0,
            "strategy": strategy,
            "breakdown": []
        }

    total_staked = 0.0
    total_payout = 0.0
    wins = 0
    places = 0

    value_staked = 0.0
    value_payout = 0.0
    value_wins = 0

    breakdown = []

    for race in history_records:
        preds = race.get("predictions", [])
        results = race.get("actual_results", [])
        odds = race.get("actual_odds", {})

        if not preds or not results:
            continue

        winner_num = results[0] if len(results) > 0 else None
        top3_nums = set(results[:3]) if len(results) >= 3 else set(results)

        top_predicted = preds[0]
        top_num = top_predicted.get("num")

        # Simple Gagnant calculation
        stake = flat_stake
        total_staked += stake

        is_win = (top_num == winner_num)
        is_place = (top_num in top3_nums)

        payout = 0.0
        if is_win:
            wins += 1
            win_odds = odds.get(top_num, top_predicted.get("cote", 2.0))
            payout = stake * win_odds
        elif is_place:
            places += 1
            place_odds = max(1.1, (odds.get(top_num, top_predicted.get("cote", 2.0)) or 2.0) * 0.35)
            payout = stake * place_odds

        total_payout += payout

        # Value bet tracking
        for runner in preds:
            if runner.get("is_value_bet"):
                v_num = runner.get("num")
                v_stake = flat_stake * (runner.get("kelly_stake_pct", 2.0) / 2.0)
                value_staked += v_stake
                if v_num == winner_num:
                    value_wins += 1
                    v_odds = odds.get(v_num, runner.get("cote", 4.0))
                    value_payout += v_stake * v_odds

        breakdown.append({
            "race_id": race.get("race_id", "R1C1"),
            "date": race.get("date", ""),
            "top_predicted": top_num,
            "winner": winner_num,
            "is_win": is_win,
            "staked": stake,
            "payout": round(payout, 2)
        })

    net_profit = round(total_payout - total_staked, 2)
    roi_pct = round((net_profit / total_staked * 100.0), 2) if total_staked > 0 else 0.0
    win_rate_pct = round((wins / total_races * 100.0), 1) if total_races > 0 else 0.0
    placed_rate_pct = round(((wins + places) / total_races * 100.0), 1) if total_races > 0 else 0.0

    value_profit = value_payout - value_staked
    value_bet_roi_pct = round((value_profit / value_staked * 100.0), 2) if value_staked > 0 else 0.0

    return {
        "total_races": total_races,
        "total_staked": round(total_staked, 2),
        "total_payout": round(total_payout, 2),
        "net_profit": net_profit,
        "roi_pct": roi_pct,
        "win_rate_pct": win_rate_pct,
        "placed_rate_pct": placed_rate_pct,
        "value_bet_staked": round(value_staked, 2),
        "value_bet_roi_pct": value_bet_roi_pct,
        "strategy": strategy,
        "breakdown": breakdown
    }


def generate_mock_backtest_data(num_races: int = 30) -> List[Dict[str, Any]]:
    """Generates realistic mock historical race data for demonstration and testing."""
    import random

    mock_races = []
    for i in range(1, num_races + 1):
        num_runners = random.randint(8, 16)
        runner_nums = list(range(1, num_runners + 1))
        random.shuffle(runner_nums)

        # Predictions (sorted by model score)
        predictions = []
        for idx, r_num in enumerate(runner_nums):
            prob = max(3.0, 35.0 - (idx * 2.5) + random.uniform(-2, 2))
            cote = round(max(1.8, 100.0 / prob + random.uniform(-1, 2)), 1)
            is_vb = (cote >= 3.5 and random.random() > 0.6)

            predictions.append({
                "num": r_num,
                "nom": f"CHEVAL_{r_num}",
                "cote": cote,
                "prob_victoire": round(prob, 1),
                "is_value_bet": is_vb,
                "kelly_stake_pct": round(random.uniform(1.0, 4.0), 1) if is_vb else 0.0
            })

        # Actual results: favorite wins 45% of time, top 3 in 75%
        if random.random() < 0.45:
            winner = runner_nums[0]
        elif random.random() < 0.80:
            winner = random.choice(runner_nums[1:3])
        else:
            winner = random.choice(runner_nums[3:])

        remaining = [r for r in runner_nums if r != winner]
        random.shuffle(remaining)
        actual_results = [winner] + remaining[:4]

        actual_odds = {p["num"]: p["cote"] for p in predictions}

        mock_races.append({
            "race_id": f"R1C{i}",
            "date": f"2025-02-{(i % 20) + 1:02d}",
            "predictions": predictions,
            "actual_results": actual_results,
            "actual_odds": actual_odds
        })

    return mock_races
