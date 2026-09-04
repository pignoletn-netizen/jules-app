import io
import csv
import logging
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from backend.models import (
    Account, Position, PortfolioSummary, TaxSimulation,
    ArbitrageRecommendation, PeaDcaGuide, StructuredProduct,
    MarketNewsItem, AnalystConsensus, AcademyConcept, CsvImportRequest
)
from backend.services.market_data import fetch_current_prices, get_analyst_consensus, ASSET_METADATA
from backend.services.advisory import (
    calculate_flat_tax, evaluate_structured_product,
    generate_pea_dca_guide, generate_arbitrage_recommendations,
    get_academy_concepts, get_market_news
)

logger = logging.getLogger("wealth_advisor")

app = FastAPI(
    title="Wealth Management & Long-Term Investment Advisory API",
    description="Application de gestion de patrimoine et conseil en investissement boursier orientée long terme (15-20 ans)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store initialized with user's initial portfolio specification
DEFAULT_ACCOUNTS: Dict[str, Account] = {
    "pea": Account(
        id="pea",
        name="PEA Fortuneo (Offre Starter)",
        broker="Fortuneo",
        account_type="PEA",
        cash_balance=100.0,
        is_active_for_deposits=True,
        monthly_deposit_target=100.0,
        api_sync_status="CONNECTED",
        last_synced="En direct",
        positions=[]
    ),
    "goliaths": Account(
        id="goliaths",
        name="Compte Goliaths",
        broker="Goliaths",
        account_type="CTO",
        cash_balance=0.0,
        is_active_for_deposits=False,
        monthly_deposit_target=0.0,
        api_sync_status="MANUAL",
        last_synced="En direct",
        positions=[
            Position(ticker="GOOGL", name="Alphabet Inc. (Google)", units=1.0, buy_price=162.60, currency="EUR", sector="Technologie / Services Média", country="États-Unis"),
            Position(ticker="WPEA.PA", name="iShares MSCI World PEA ETF", units=22.73, buy_price=5.85, currency="EUR", sector="Diversifié Mondial", country="Mondial", asset_type="ETF"),
            Position(ticker="KO", name="The Coca-Cola Company", units=0.18, buy_price=63.33, currency="EUR", sector="Consommation Défensive", country="États-Unis"),
            Position(ticker="TSM", name="TSMC", units=0.06, buy_price=183.00, currency="EUR", sector="Semi-conducteurs", country="Taïwan"),
            Position(ticker="MSFT", name="Microsoft Corporation", units=0.025, buy_price=405.20, currency="EUR", sector="Technologie / Logiciel", country="États-Unis"),
            Position(ticker="AMZN", name="Amazon.com Inc.", units=0.06, buy_price=165.50, currency="EUR", sector="Commerce Électronique / Cloud", country="États-Unis"),
        ]
    ),
    "trading212": Account(
        id="trading212",
        name="Compte Trading 212",
        broker="Trading 212",
        account_type="CTO",
        cash_balance=0.0,
        is_active_for_deposits=False,
        monthly_deposit_target=0.0,
        api_sync_status="CONNECTED",
        last_synced="En direct",
        positions=[
            Position(ticker="VWCE.DE", name="Vanguard FTSE All-World ETF", units=5.48, buy_price=128.55, currency="EUR", sector="Diversifié Mondial", country="Mondial", asset_type="ETF"),
            Position(ticker="NVDA", name="NVIDIA Corporation", units=2.0, buy_price=117.36, currency="EUR", sector="Technologie / IA & GPU", country="États-Unis"),
            Position(ticker="GOOGL", name="Alphabet Inc. (Google)", units=0.80, buy_price=163.51, currency="EUR", sector="Technologie / Services Média", country="États-Unis"),
        ]
    )
}

# State holder
portfolio_db = DEFAULT_ACCOUNTS.copy()

def _calculate_account_positions(account: Account, prices: Dict[str, float]) -> Account:
    """Updates live current price, total value, and gain/loss metrics for an account."""
    updated_positions = []
    positions_value_total = 0.0

    for pos in account.positions:
        live_price = prices.get(pos.ticker, pos.buy_price)
        total_val = round(pos.units * live_price, 2)
        cost_basis = round(pos.units * pos.buy_price, 2)
        gain_loss = round(total_val - cost_basis, 2)
        gain_loss_pct = round((gain_loss / cost_basis * 100.0), 2) if cost_basis > 0 else 0.0

        updated_pos = pos.model_copy(update={
            "current_price": live_price,
            "total_value": total_val,
            "gain_loss": gain_loss,
            "gain_loss_percent": gain_loss_pct
        })
        updated_positions.append(updated_pos)
        positions_value_total += total_val

    struct_val = 0.0
    if account.id == "goliaths":
        struct_prod = evaluate_structured_product(prices)
        account.structured_product = struct_prod
        struct_val = struct_prod.current_value

    tot_account_val = round(account.cash_balance + positions_value_total + struct_val, 2)

    return account.model_copy(update={
        "positions": updated_positions,
        "total_value": tot_account_val
    })

@app.get("/api/portfolio", response_model=PortfolioSummary)
def get_portfolio_summary():
    """Returns global wealth overview, accounts breakdown, and sector/geographic allocations."""
    all_tickers = ["WPEA.PA", "GOOGL", "KO", "TSM", "MSFT", "AMZN", "HAL", "VLO", "PBR", "DVN", "VWCE.DE", "NVDA"]
    live_prices = fetch_current_prices(all_tickers)

    updated_accounts: List[Account] = []
    total_wealth = 0.0
    cash_total = 0.0
    invested_total = 0.0
    total_cost_basis = 0.0

    sector_totals: Dict[str, float] = {}
    geo_totals: Dict[str, float] = {}

    for acc_id, acc in portfolio_db.items():
        updated_acc = _calculate_account_positions(acc, live_prices)
        updated_accounts.append(updated_acc)

        total_wealth += updated_acc.total_value
        cash_total += updated_acc.cash_balance

        for pos in updated_acc.positions:
            invested_total += pos.total_value
            total_cost_basis += pos.units * pos.buy_price

            sector_totals[pos.sector] = round(sector_totals.get(pos.sector, 0.0) + pos.total_value, 2)
            geo_totals[pos.country] = round(geo_totals.get(pos.country, 0.0) + pos.total_value, 2)

        if updated_acc.structured_product:
            sp_val = updated_acc.structured_product.current_value
            invested_total += sp_val
            total_cost_basis += updated_acc.structured_product.invested_amount
            sector_totals["Pétrole & Énergie (Produit Structuré)"] = round(sector_totals.get("Pétrole & Énergie (Produit Structuré)", 0.0) + sp_val, 2)
            geo_totals["Mondial / Énergie"] = round(geo_totals.get("Mondial / Énergie", 0.0) + sp_val, 2)

    total_gain_loss = round(invested_total - total_cost_basis, 2)
    total_gain_loss_percent = round((total_gain_loss / total_cost_basis * 100.0), 2) if total_cost_basis > 0 else 0.0

    return PortfolioSummary(
        total_wealth=round(total_wealth, 2),
        cash_total=round(cash_total, 2),
        invested_total=round(invested_total, 2),
        total_gain_loss=total_gain_loss,
        total_gain_loss_percent=total_gain_loss_percent,
        accounts=updated_accounts,
        sector_allocation=sector_totals,
        geo_allocation=geo_totals
    )

@app.get("/api/quotes")
def get_quotes():
    """Returns current market quotes for portfolio assets."""
    all_tickers = ["WPEA.PA", "GOOGL", "KO", "TSM", "MSFT", "AMZN", "HAL", "VLO", "PBR", "DVN", "VWCE.DE", "NVDA"]
    return fetch_current_prices(all_tickers)

@app.get("/api/advisory/pea-dca", response_model=PeaDcaGuide)
def get_pea_dca_recommendation(monthly_deposit: float = 100.0):
    """Calculates monthly DCA order execution for Fortuneo Starter PEA."""
    pea_acc = portfolio_db.get("pea")
    pea_cash = pea_acc.cash_balance if pea_acc else 100.0
    prices = fetch_current_prices(["WPEA.PA"])
    wpea_price = prices.get("WPEA.PA", 5.85)

    return generate_pea_dca_guide(pea_cash=pea_cash, monthly_deposit=monthly_deposit, wpea_price=wpea_price)

@app.get("/api/advisory/structured-product", response_model=StructuredProduct)
def get_structured_product_status():
    """Returns real-time status and protection barrier monitoring for the Oil Structured Product."""
    prices = fetch_current_prices(["HAL", "VLO", "PBR", "DVN"])
    return evaluate_structured_product(prices)

@app.get("/api/advisory/tax-simulation", response_model=TaxSimulation)
def simulate_tax(sell_units: float, buy_price: float, current_price: float, ticker: str = "ASSET"):
    """Simulates 30% Flat Tax impact on a potential sale."""
    return calculate_flat_tax(sell_units, buy_price, current_price, ticker)

@app.get("/api/advisory/arbitrage", response_model=List[ArbitrageRecommendation])
def get_arbitrage_recommendations():
    """Returns strategic 4-year horizon (2026-2030) capital rebalancing recommendations."""
    goliaths_val = portfolio_db["goliaths"].total_value if "goliaths" in portfolio_db else 800.0
    t212_val = portfolio_db["trading212"].total_value if "trading212" in portfolio_db else 1000.0
    return generate_arbitrage_recommendations(goliaths_val, t212_val)

@app.get("/api/news", response_model=List[MarketNewsItem])
def get_news():
    """Returns market news, geopolitical analysis, and sector trends."""
    return get_market_news()

@app.get("/api/consensus", response_model=List[AnalystConsensus])
def get_consensus():
    """Returns analyst consensus recommendations and target price upsides."""
    return get_analyst_consensus()

@app.get("/api/academy", response_model=List[AcademyConcept])
def get_academy():
    """Returns beginner financial concepts for investor education."""
    return get_academy_concepts()

@app.post("/api/account/{account_id}/sync-toggle")
def toggle_account_sync(account_id: str, mode: str):
    """Toggles broker sync mode between API CONNECTED and MANUAL mode."""
    if account_id not in portfolio_db:
        raise HTTPException(status_code=404, detail="Compte non trouvé")

    acc = portfolio_db[account_id]
    portfolio_db[account_id] = acc.model_copy(update={
        "api_sync_status": mode.upper(),
        "last_synced": "Mise à jour manuelle" if mode == "MANUAL" else "En direct"
    })
    return {"message": f"Mode de synchronisation mis à jour pour {acc.name}", "status": mode}

@app.post("/api/sync/csv")
async def import_csv_positions(file: UploadFile = File(...), account_id: str = "goliaths"):
    """Parses uploaded CSV file and imports positions into the specified account."""
    if account_id not in portfolio_db:
        raise HTTPException(status_code=404, detail="Compte introuvable")

    content = await file.read()
    text = content.decode("utf-8")
    reader = csv.DictReader(io.StringIO(text))

    imported_positions = []
    for row in reader:
        ticker = row.get("ticker", "").strip().upper()
        if not ticker:
            continue
        units = float(row.get("units", row.get("quantité", 1)))
        buy_price = float(row.get("buy_price", row.get("prix_achat", 100)))
        name = row.get("name", ticker)

        meta = ASSET_METADATA.get(ticker, {})
        sector = meta.get("sector", row.get("sector", "Diversifié"))
        country = meta.get("country", row.get("country", "Mondial"))

        imported_positions.append(
            Position(
                ticker=ticker,
                name=name,
                units=units,
                buy_price=buy_price,
                sector=sector,
                country=country
            )
        )

    if imported_positions:
        portfolio_db[account_id] = portfolio_db[account_id].model_copy(update={
            "positions": imported_positions,
            "api_sync_status": "MANUAL_CSV_IMPORTED",
            "last_synced": "Import CSV réussi"
        })

    return {"message": f"{len(imported_positions)} positions importées avec succès", "positions_count": len(imported_positions)}
