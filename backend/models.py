from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class Position(BaseModel):
    ticker: str
    name: str
    units: float
    buy_price: float
    current_price: float = 0.0
    currency: str = "EUR"
    asset_type: str = "Stock"  # Stock, ETF, Structured Product
    sector: str = "Diversified"
    country: str = "Global"
    total_value: float = 0.0
    gain_loss: float = 0.0
    gain_loss_percent: float = 0.0

class StructuredProductUnderlying(BaseModel):
    ticker: str
    name: str
    initial_price: float
    current_price: float
    price_change_pct: float
    barrier_price: float  # -40% from initial price
    distance_to_barrier_pct: float  # percentage remaining until barrier is hit
    is_barrier_breached: bool = False

class StructuredProduct(BaseModel):
    name: str = "Produit Structuré Pétrole 2030"
    invested_amount: float = 493.02
    current_value: float = 493.02
    maturity_date: str = "2030-03-15"
    protection_barrier_pct: float = -40.0
    underlyings: List[StructuredProductUnderlying] = []
    worst_underlying_pct: float = 0.0
    status: str = "SECURE"  # SECURE, WARNING, BREACHED
    alert_message: str = ""

class Account(BaseModel):
    id: str
    name: str
    broker: str
    account_type: str  # PEA, CTO
    cash_balance: float = 0.0
    positions: List[Position] = []
    total_value: float = 0.0
    is_active_for_deposits: bool = False
    monthly_deposit_target: float = 0.0
    api_sync_status: str = "CONNECTED"  # CONNECTED, DISCONNECTED, MANUAL, PARTIAL
    last_synced: str = "En direct"
    structured_product: Optional[StructuredProduct] = None

class PortfolioSummary(BaseModel):
    total_wealth: float
    cash_total: float
    invested_total: float
    total_gain_loss: float
    total_gain_loss_percent: float
    accounts: List[Account]
    sector_allocation: Dict[str, float]
    geo_allocation: Dict[str, float]

class TaxSimulation(BaseModel):
    ticker: str
    sell_units: float
    buy_price: float
    current_price: float
    gross_proceeds: float
    gross_gain: float
    flat_tax_rate: float = 0.30  # 30% Flat Tax (12.8% IR + 17.2% Social)
    tax_amount: float
    net_gain: float
    net_proceeds: float

class ArbitrageRecommendation(BaseModel):
    id: str
    account_id: str
    account_name: str
    action: str  # REBALANCE, HOLD, CONSOLIDATE
    from_ticker: Optional[str] = None
    to_ticker: Optional[str] = None
    units: Optional[float] = None
    estimated_amount: float
    estimated_tax: float
    net_amount_after_tax: float
    horizon_years: int = 4  # target 2030
    title: str
    rationale: str
    risk_impact: str  # LOWER_RISK, OPTIMIZE_YIELD, STREAMLINE

class PeaDcaGuide(BaseModel):
    monthly_deposit: float
    recommended_etf_ticker: str = "WPEA.PA"
    recommended_etf_name: str = "iShares MSCI World Swap PEA UCITS ETF"
    etf_price: float
    affordable_units: int
    total_order_cost: float
    remaining_cash: float
    fortuneo_fee: float = 0.0  # 0€ for 1st order <= 500€/month on Starter
    is_fee_free: bool = True
    next_action_date: str
    recommendation_summary: str

class MarketNewsItem(BaseModel):
    id: str
    title: str
    source: str
    url: str
    published_at: str
    summary: str
    geopolitical_impact: str
    impact_level: str  # HIGH, MEDIUM, LOW
    relevant_tickers: List[str]

class AnalystConsensus(BaseModel):
    ticker: str
    company_name: str
    target_price_avg: float
    current_price: float
    upside_potential_pct: float
    recommendation: str  # Strong Buy, Buy, Hold, Sell
    num_analysts: int

class AcademyConcept(BaseModel):
    id: str
    title: str
    short_definition: str
    detailed_explanation: str
    concrete_example: str
    category: str  # Fiscalité, Stratégie, Produits, Risques
    key_takeaway: str

class CsvImportRequest(BaseModel):
    account_id: str
    csv_content: str
