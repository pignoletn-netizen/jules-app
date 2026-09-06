from typing import Dict, Any, List

def format_horse_str(h: Dict[str, Any]) -> str:
    num = h.get("num")
    nom = h.get("nom", "")
    cote = h.get("cote")
    cote_str = f" (cote: {cote})" if cote else ""
    value_str = " 🔥 VALUE" if h.get("is_value_bet") else ""
    return f"N°{num} {nom}{cote_str}{value_str}"

def generate_pmu_bet_recommendations(predicted_race: Dict[str, Any]) -> Dict[str, Any]:
    raw_ranked = predicted_race.get("ranked_runners", [])

    # Filter out non-runners (NON_PARTANT)
    ranked = [
        r for r in raw_ranked
        if not (
            r.get("non_partant") is True or
            r.get("est_non_partant") is True or
            str(r.get("statut", "")).upper() in ("NON_PARTANT", "NONPARTANT") or
            str(r.get("statutPmu", "")).upper() in ("NON_PARTANT", "NONPARTANT")
        )
    ]

    if not ranked or len(ranked) < 2:
        return {"error": "Insuffisant de partants pour générer des mises"}

    top1 = ranked[0]
    top2 = ranked[1]
    top3 = ranked[2] if len(ranked) > 2 else top2
    top4 = ranked[3] if len(ranked) > 3 else top3
    top5 = ranked[4] if len(ranked) > 4 else top4
    top6 = ranked[5] if len(ranked) > 5 else top5
    top7 = ranked[6] if len(ranked) > 6 else top6
    top8 = ranked[7] if len(ranked) > 7 else top7

    def unique_nums(runners_list):
        seen = set()
        out = []
        for r in runners_list:
            n = r.get("num")
            if n is not None and n not in seen:
                seen.add(n)
                out.append(n)
        return out

    value_bets = [r for r in ranked if r.get("is_value_bet")]
    best_value = value_bets[0] if value_bets else None

    outsiders = [r for r in ranked[3:] if r.get("cote") and float(r.get("cote")) >= 7.0]
    best_outsider = outsiders[0] if outsiders else (ranked[3] if len(ranked) > 3 else top2)

    top_8_unique = unique_nums(ranked[:8])
    associes_trio = unique_nums([r for r in [top3, top4, best_value or best_outsider] if r.get("num") not in (top1.get("num"), top2.get("num"))])

    stake_advice = ""
    if best_value:
        stake_advice = f"Pari Spéculatif conseillé: N°{best_value.get('num')} ({best_value.get('nom')}) est une Value Bet avec un niveau de mise de {best_value.get('kelly_stake_pct')}% de bankroll."
    else:
        stake_advice = f"Pari de Sécurité: Mise modérée sur le favori N°{top1.get('num')} ({top1.get('nom')}) (1 unit)."

    bets = {
        "simple_gagnant": {
            "favori": format_horse_str(top1),
            "value_bet": format_horse_str(best_value) if best_value else format_horse_str(best_outsider),
            "conseil": f"Miser Simple Gagnant principal sur le N°{top1.get('num')} ({top1.get('nom')}). {stake_advice}"
        },
        "simple_place": {
            "chevaux": [format_horse_str(top1), format_horse_str(top2), format_horse_str(top3)],
            "conseil": f"Base solide Placé: N°{top1.get('num')} et N°{top2.get('num')} (Proba placé > {top1.get('prob_place', 0)}%)."
        },
        "couple": {
            "couple_gagnant": f"N°{top1.get('num')} - N°{top2.get('num')}",
            "couple_place": f"N°{top1.get('num')} - N°{top2.get('num')} / N°{top1.get('num')} - N°{top3.get('num')}",
            "couple_ordre": f"1er: N°{top1.get('num')} / 2ème: N°{top2.get('num')}",
            "combinaison_elargie": unique_nums([top1, top2, top3, best_value or best_outsider])
        },
        "deux_sur_quatre": {
            "selections": unique_nums([top1, top2, top3, top4]),
            "conseil": f"Sélection 2 sur 4: N°{top1.get('num')} - N°{top2.get('num')} - N°{top3.get('num')} - N°{top4.get('num')}"
        },
        "trio": {
            "base": f"N°{top1.get('num')} - N°{top2.get('num')}",
            "associes": associes_trio,
            "ticket_champ_reduit": f"Base (N°{top1.get('num')} - N°{top2.get('num')}) avec X = {associes_trio}"
        },
        "tierce": {
            "ordre_probable": f"1er: N°{top1.get('num')} / 2ème: N°{top2.get('num')} / 3ème: N°{top3.get('num')}",
            "combinaison": unique_nums([top1, top2, top3, top4])
        },
        "quarte": {
            "selections": unique_nums([top1, top2, top3, top4, top5]),
            "base_solide": f"N°{top1.get('num')} - N°{top2.get('num')} - N°{top3.get('num')}"
        },
        "quinte": {
            "pronostic_8_chevaux": top_8_unique,
            "base_quinte": f"Base: N°{top1.get('num')} - N°{top2.get('num')} - N°{top3.get('num')}",
            "complementaires": unique_nums([top4, top5, top6, best_value or best_outsider])
        },
        "multi": {
            "multi_en_4": unique_nums([top1, top2, top3, top4]),
            "multi_en_5": unique_nums([top1, top2, top3, top4, top5]),
            "multi_en_6": unique_nums([top1, top2, top3, top4, top5, top6]),
            "multi_en_7": unique_nums([top1, top2, top3, top4, top5, top6, top7])
        }
    }

    return bets
