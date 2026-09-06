import requests
import datetime
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

BASE_URL = "https://online.turfinfo.api.pmu.fr/rest/client/7/programme"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def format_date(date_str: Optional[str] = None) -> str:
    if not date_str or date_str.lower() in ("today", "aujourdhui"):
        return datetime.datetime.now().strftime("%d%m%Y")
    if "-" in date_str:
        parts = date_str.split("-")
        if len(parts) == 3:
            return f"{parts[2]}{parts[1]}{parts[0]}"
    return date_str.replace("/", "").replace("-", "")

def get_daily_programme(date_str: Optional[str] = None) -> Dict[str, Any]:
    formatted_date = format_date(date_str)
    url = f"{BASE_URL}/{formatted_date}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error(f"Error fetching PMU programme for {formatted_date}: {e}")
        return {}

def get_race_details(date_str: str, num_reunion: int, num_course: int) -> Dict[str, Any]:
    formatted_date = format_date(date_str)
    url = f"{BASE_URL}/{formatted_date}/R{num_reunion}/C{num_course}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error(f"Error fetching race details for {formatted_date} R{num_reunion}C{num_course}: {e}")
        return {}

def get_race_participants(date_str: str, num_reunion: int, num_course: int) -> List[Dict[str, Any]]:
    formatted_date = format_date(date_str)
    url = f"{BASE_URL}/{formatted_date}/R{num_reunion}/C{num_course}/participants"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get("participants", [])
    except Exception as e:
        logger.error(f"Error fetching participants for {formatted_date} R{num_reunion}C{num_course}: {e}")
        return []

def get_parsed_race_data(date_str: Optional[str] = None, num_reunion: int = 1, num_course: int = 1) -> Dict[str, Any]:
    date_formatted = format_date(date_str)
    race_info = get_race_details(date_formatted, num_reunion, num_course)
    participants = get_race_participants(date_formatted, num_reunion, num_course)

    processed_participants = []
    for p in participants:
        last_odds = p.get("dernierRapportDirect", {}).get("rapport")
        reduction_kilometrique = p.get("reductionKilometrique")
        speed_str = ""
        if reduction_kilometrique:
            speed_str = f"{reduction_kilometrique} s/km"

        num_val = p.get("numPmu") or p.get("numOrdre") or p.get("numProno")
        processed_participants.append({
            "num": num_val,
            "nom": p.get("nom"),
            "age": p.get("age"),
            "sexe": p.get("sexe"),
            "musique": p.get("musique", ""),
            "driver": p.get("driver"),
            "entraineur": p.get("entraineur"),
            "proprio": p.get("proprietaire"),
            "gain": p.get("gainsParticipant", {}).get("gainsCarriere", 0) / 100 if isinstance(p.get("gainsParticipant"), dict) else 0,
            "cote": last_odds,
            "handicapPoids": p.get("handicapPoids"),
            "deferre": p.get("deferre"),
            "reductionKilometrique": reduction_kilometrique,
            "speed_str": speed_str,
            "oeilleres": p.get("oeilleres"),
            "statut": p.get("statut"),
            "engagement": p.get("engagement", True)
        })

    hippodrome = race_info.get("hippodrome", {})
    hippo_name = (hippodrome.get("libelleCourt") or hippodrome.get("libelleLong") or "Hippodrome") if isinstance(hippodrome, dict) else "Hippodrome"
    piste = race_info.get("piste", {})
    piste_nature = piste.get("naturePiste") if isinstance(piste, dict) else "SYNTHETIQUE/HERBE"

    return {
        "date": date_formatted,
        "reunion": num_reunion,
        "course": num_course,
        "libelle": race_info.get("libelle", f"Course {num_course}"),
        "discipline": race_info.get("discipline", "INCONNU"),
        "distance": race_info.get("distance", 0),
        "montantPrix": race_info.get("montantPrix", 0),
        "hippodrome": hippo_name,
        "terrain": piste_nature,
        "corde": race_info.get("corde"),
        "conditions": race_info.get("conditions", ""),
        "nombreDeclaresPartants": race_info.get("nombreDeclaresPartants", len(participants)),
        "participants": processed_participants
    }
