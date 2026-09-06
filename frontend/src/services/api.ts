export interface RaceSummary {
  num: number;
  reunion: number;
  libelle: string;
  discipline: string;
  distance: number;
  heureDepart: number;
  nombrePartants: number;
}

export interface Reunion {
  num: number;
  hippodrome: string;
  pays: string;
  disciplines: string[];
  courses: RaceSummary[];
}

export interface DailyProgramme {
  date: string;
  reunions: Reunion[];
}

export interface Runner {
  num: number;
  nom: string;
  age: number;
  sexe: string;
  musique: string;
  driver: string;
  entraineur: string;
  cote: number | null;
  deferre?: string;
  oeilleres?: string;
  speed_str?: string;
  raw_score: number;
  prob_victoire: number;
  prob_place: number;
  predicted_rank: number;
  is_value_bet?: boolean;
  value_ratio?: number;
  kelly_stake_pct?: number;
}

export interface PMUBets {
  simple_gagnant: {
    favori: string;
    value_bet: string;
    conseil: string;
  };
  simple_place: {
    chevaux: string[];
    conseil: string;
  };
  couple: {
    couple_gagnant: string;
    couple_place: string;
    couple_ordre: string;
    combinaison_elargie: number[];
  };
  deux_sur_quatre: {
    selections: number[];
    conseil: string;
  };
  trio: {
    base: string;
    associes: number[];
    ticket_champ_reduit: string;
  };
  tierce: {
    ordre_probable: string;
    combinaison: number[];
  };
  quarte: {
    selections: number[];
    base_solide: string;
  };
  quinte: {
    pronostic_8_chevaux: number[];
    base_quinte: string;
    complementaires: number[];
  };
  multi: {
    multi_en_4: number[];
    multi_en_5: number[];
    multi_en_6: number[];
    multi_en_7: number[];
  };
}

export interface RaceAnalysis {
  race_info: {
    date: string;
    reunion: number;
    course: number;
    libelle: string;
    discipline: string;
    distance: number;
    hippodrome: string;
    terrain: string;
    corde: string;
    conditions: string;
    nombrePartants: number;
    confidence: string;
  };
  ranked_runners: Runner[];
  pmu_bets: PMUBets;
}

export interface DailySummaryItem {
  reunion: number;
  course: number;
  hippodrome: string;
  libelle: string;
  discipline: string;
  distance: number;
  confidence: string;
  has_value_bets?: boolean;
  top_runners: Array<{
    num: number;
    nom: string;
    prob_victoire: number;
    cote: number | null;
    is_value_bet?: boolean;
    kelly_stake_pct?: number;
  }>;
  bets_preview: {
    simple_favori: string;
    simple_outsider: string;
    trio_base: string;
    quinte_base: string;
    multi_4: number[];
  };
}

export interface DailySummary {
  date: string;
  summary: DailySummaryItem[];
}

export interface BacktestMetrics {
  total_races: number;
  total_staked: number;
  total_payout: number;
  net_profit: number;
  roi_pct: number;
  win_rate_pct: number;
  placed_rate_pct: number;
  value_bet_staked: number;
  value_bet_roi_pct: number;
  strategy: string;
  breakdown: Array<{
    race_id: string;
    date: string;
    top_predicted: number;
    winner: number;
    is_win: boolean;
    staked: number;
    payout: number;
  }>;
}

export interface BacktestResponse {
  period_days: number;
  metrics: BacktestMetrics;
  recent_history: any[];
}

const getApiBaseUrl = () => {
  if (typeof window !== "undefined") {
    const host = window.location.hostname || "127.0.0.1";
    return `${window.location.protocol}//${host}:8000/api`;
  }
  return "http://127.0.0.1:8000/api";
};

export async function fetchDailyProgramme(date?: string): Promise<DailyProgramme> {
  const baseUrl = getApiBaseUrl();
  const url = date ? `${baseUrl}/races/today?date=${date}` : `${baseUrl}/races/today`;
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new Error("Erreur de chargement du programme");
  return res.json();
}

export async function fetchRaceAnalysis(date: string, reunion: number, course: number): Promise<RaceAnalysis> {
  const baseUrl = getApiBaseUrl();
  const res = await fetch(`${baseUrl}/races/${date}/${reunion}/${course}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Erreur de chargement de l'analyse de la course");
  return res.json();
}

export async function fetchDailyPMUSummary(date?: string): Promise<DailySummary> {
  const baseUrl = getApiBaseUrl();
  const url = date ? `${baseUrl}/summary/today?date=${date}` : `${baseUrl}/summary/today`;
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new Error("Erreur de chargement du récapitulatif des mises PMU");
  return res.json();
}

export async function fetchBacktestData(days: number = 30): Promise<BacktestResponse> {
  const baseUrl = getApiBaseUrl();
  const res = await fetch(`${baseUrl}/backtest?days=${days}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Erreur de chargement des résultats de backtest");
  return res.json();
}
