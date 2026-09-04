const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api";

export interface Position {
  ticker: string;
  name: string;
  units: number;
  buy_price: number;
  current_price: number;
  currency: string;
  asset_type: string;
  sector: string;
  country: string;
  total_value: number;
  gain_loss: number;
  gain_loss_percent: number;
}

export interface StructuredProductUnderlying {
  ticker: string;
  name: string;
  initial_price: number;
  current_price: number;
  price_change_pct: number;
  barrier_price: number;
  distance_to_barrier_pct: number;
  is_barrier_breached: boolean;
}

export interface StructuredProduct {
  name: string;
  invested_amount: number;
  current_value: number;
  maturity_date: string;
  protection_barrier_pct: number;
  underlyings: StructuredProductUnderlying[];
  worst_underlying_pct: number;
  status: "SECURE" | "WARNING" | "BREACHED";
  alert_message: string;
}

export interface Account {
  id: string;
  name: string;
  broker: string;
  account_type: "PEA" | "CTO";
  cash_balance: number;
  positions: Position[];
  total_value: number;
  is_active_for_deposits: boolean;
  monthly_deposit_target: number;
  api_sync_status: string;
  last_synced: string;
  structured_product?: StructuredProduct;
}

export interface PortfolioSummary {
  total_wealth: number;
  cash_total: number;
  invested_total: number;
  total_gain_loss: number;
  total_gain_loss_percent: number;
  accounts: Account[];
  sector_allocation: Record<string, number>;
  geo_allocation: Record<string, number>;
}

export interface TaxSimulation {
  ticker: string;
  sell_units: number;
  buy_price: number;
  current_price: number;
  gross_proceeds: number;
  gross_gain: number;
  flat_tax_rate: number;
  tax_amount: number;
  net_gain: number;
  net_proceeds: number;
}

export interface ArbitrageRecommendation {
  id: string;
  account_id: string;
  account_name: string;
  action: string;
  from_ticker?: string;
  to_ticker?: string;
  units?: number;
  estimated_amount: number;
  estimated_tax: number;
  net_amount_after_tax: number;
  horizon_years: number;
  title: string;
  rationale: string;
  risk_impact: string;
}

export interface PeaDcaGuide {
  monthly_deposit: number;
  recommended_etf_ticker: string;
  recommended_etf_name: string;
  etf_price: number;
  affordable_units: number;
  total_order_cost: number;
  remaining_cash: number;
  fortuneo_fee: number;
  is_fee_free: boolean;
  next_action_date: string;
  recommendation_summary: string;
}

export interface MarketNewsItem {
  id: string;
  title: string;
  source: string;
  url: string;
  published_at: string;
  summary: string;
  geopolitical_impact: string;
  impact_level: "HIGH" | "MEDIUM" | "LOW";
  relevant_tickers: string[];
}

export interface AnalystConsensus {
  ticker: string;
  company_name: string;
  target_price_avg: number;
  current_price: number;
  upside_potential_pct: number;
  recommendation: string;
  num_analysts: number;
}

export interface AcademyConcept {
  id: string;
  title: string;
  short_definition: string;
  detailed_explanation: string;
  concrete_example: string;
  category: string;
  key_takeaway: string;
}

export async function fetchPortfolioSummary(): Promise<PortfolioSummary> {
  const res = await fetch(`${API_BASE_URL}/portfolio`);
  if (!res.ok) throw new Error("Erreur de chargement du portefeuille");
  return res.json();
}

export async function fetchPeaDcaGuide(monthlyDeposit: number = 100): Promise<PeaDcaGuide> {
  const res = await fetch(`${API_BASE_URL}/advisory/pea-dca?monthly_deposit=${monthlyDeposit}`);
  if (!res.ok) throw new Error("Erreur de chargement des recommandations PEA");
  return res.json();
}

export async function fetchStructuredProduct(): Promise<StructuredProduct> {
  const res = await fetch(`${API_BASE_URL}/advisory/structured-product`);
  if (!res.ok) throw new Error("Erreur de chargement du produit structuré");
  return res.json();
}

export async function simulateFlatTax(sellUnits: number, buyPrice: number, currentPrice: number, ticker: string = "ASSET"): Promise<TaxSimulation> {
  const res = await fetch(`${API_BASE_URL}/advisory/tax-simulation?sell_units=${sellUnits}&buy_price=${buyPrice}&current_price=${currentPrice}&ticker=${ticker}`);
  if (!res.ok) throw new Error("Erreur de simulation fiscale");
  return res.json();
}

export async function fetchArbitrageRecommendations(): Promise<ArbitrageRecommendation[]> {
  const res = await fetch(`${API_BASE_URL}/advisory/arbitrage`);
  if (!res.ok) throw new Error("Erreur des recommandations d'arbitrage");
  return res.json();
}

export async function fetchMarketNews(): Promise<MarketNewsItem[]> {
  const res = await fetch(`${API_BASE_URL}/news`);
  if (!res.ok) throw new Error("Erreur des actualités boursières");
  return res.json();
}

export async function fetchAnalystConsensus(): Promise<AnalystConsensus[]> {
  const res = await fetch(`${API_BASE_URL}/consensus`);
  if (!res.ok) throw new Error("Erreur du consensus analystes");
  return res.json();
}

export async function fetchAcademyConcepts(): Promise<AcademyConcept[]> {
  const res = await fetch(`${API_BASE_URL}/academy`);
  if (!res.ok) throw new Error("Erreur de l'académie");
  return res.json();
}

export async function toggleAccountSyncMode(accountId: string, mode: string): Promise<{ message: string; status: string }> {
  const res = await fetch(`${API_BASE_URL}/account/${accountId}/sync-toggle?mode=${mode}`, {
    method: "POST"
  });
  if (!res.ok) throw new Error("Erreur de changement de mode de synchronisation");
  return res.json();
}

export async function uploadCsvPositions(accountId: string, file: File): Promise<{ message: string; positions_count: number }> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_BASE_URL}/sync/csv?account_id=${accountId}`, {
    method: "POST",
    body: formData
  });
  if (!res.ok) throw new Error("Erreur lors de l'import du fichier CSV");
  return res.json();
}
