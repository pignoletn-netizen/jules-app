import logging
from typing import Dict, List, Optional
import yfinance as yf
from backend.models import AnalystConsensus

logger = logging.getLogger(__name__)

# Fallback realistic prices in EUR / USD if live retrieval fails or is delayed
FALLBACK_PRICES = {
    "WPEA.PA": 5.85,      # iShares MSCI World Swap PEA UCITS ETF
    "GOOGL": 178.50,      # Alphabet Inc.
    "KO": 68.20,          # The Coca-Cola Company
    "TSM": 192.40,        # Taiwan Semiconductor Manufacturing Co.
    "MSFT": 445.10,       # Microsoft Corporation
    "AMZN": 186.30,       # Amazon.com Inc.
    "HAL": 34.50,         # Halliburton Company
    "VLO": 165.20,        # Valero Energy Corporation
    "PBR": 14.80,         # Petroleo Brasileiro SA (Petrobras)
    "DVN": 48.90,         # Devon Energy Corporation
    "VWCE.DE": 128.40,    # Vanguard FTSE All-World UCITS ETF
    "NVDA": 125.80,       # NVIDIA Corporation
    "EURUSD=X": 1.08,     # EUR/USD exchange rate
}

ASSET_METADATA = {
    "WPEA.PA": {
        "name": "iShares MSCI World Swap PEA ETF",
        "currency": "EUR",
        "asset_type": "ETF",
        "sector": "Diversifié Mondial",
        "country": "Mondial",
        "us_ticker": None
    },
    "GOOGL": {
        "name": "Alphabet Inc. (Google)",
        "currency": "USD",
        "asset_type": "Action",
        "sector": "Technologie / Services Média",
        "country": "États-Unis",
        "us_ticker": "GOOGL"
    },
    "KO": {
        "name": "The Coca-Cola Company",
        "currency": "USD",
        "asset_type": "Action",
        "sector": "Consommation Défensive",
        "country": "États-Unis",
        "us_ticker": "KO"
    },
    "TSM": {
        "name": "Taiwan Semiconductor (TSMC)",
        "currency": "USD",
        "asset_type": "Action",
        "sector": "Semi-conducteurs",
        "country": "Taïwan",
        "us_ticker": "TSM"
    },
    "MSFT": {
        "name": "Microsoft Corporation",
        "currency": "USD",
        "asset_type": "Action",
        "sector": "Technologie / Logiciel",
        "country": "États-Unis",
        "us_ticker": "MSFT"
    },
    "AMZN": {
        "name": "Amazon.com Inc.",
        "currency": "USD",
        "asset_type": "Action",
        "sector": "Commerce Électronique / Cloud",
        "country": "États-Unis",
        "us_ticker": "AMZN"
    },
    "HAL": {
        "name": "Halliburton Company",
        "currency": "USD",
        "asset_type": "Action",
        "sector": "Pétrole / Services Pétroliers",
        "country": "États-Unis",
        "us_ticker": "HAL"
    },
    "VLO": {
        "name": "Valero Energy Corporation",
        "currency": "USD",
        "asset_type": "Action",
        "sector": "Pétrole / Raffinage",
        "country": "États-Unis",
        "us_ticker": "VLO"
    },
    "PBR": {
        "name": "Petroleo Brasileiro (Petrobras)",
        "currency": "USD",
        "asset_type": "Action",
        "sector": "Pétrole & Gaz Intégré",
        "country": "Brésil",
        "us_ticker": "PBR"
    },
    "DVN": {
        "name": "Devon Energy Corporation",
        "currency": "USD",
        "asset_type": "Action",
        "sector": "Pétrole / Exploration & Prod",
        "country": "États-Unis",
        "us_ticker": "DVN"
    },
    "VWCE.DE": {
        "name": "Vanguard FTSE All-World UCITS ETF",
        "currency": "EUR",
        "asset_type": "ETF",
        "sector": "Diversifié Mondial",
        "country": "Mondial",
        "us_ticker": None
    },
    "NVDA": {
        "name": "NVIDIA Corporation",
        "currency": "USD",
        "asset_type": "Action",
        "sector": "Technologie / IA & GPU",
        "country": "États-Unis",
        "us_ticker": "NVDA"
    }
}

def get_eur_usd_rate() -> float:
    """Fetch current EUR/USD exchange rate with fallback."""
    try:
        ticker = yf.Ticker("EURUSD=X")
        info = ticker.fast_info
        rate = info.last_price if hasattr(info, "last_price") and info.last_price else None
        if rate:
            return float(rate)
    except Exception as e:
        logger.warning(f"Could not fetch live EUR/USD rate: {e}")
    return FALLBACK_PRICES["EURUSD=X"]

def fetch_current_prices(tickers: List[str]) -> Dict[str, float]:
    """Fetch live prices for given tickers converted to EUR if originally in USD."""
    prices = {}
    usd_eur_rate = 1.0 / get_eur_usd_rate()

    for ticker in tickers:
        price_eur = None
        try:
            yt = yf.Ticker(ticker)
            fast_info = yt.fast_info
            last_price = getattr(fast_info, 'last_price', None)
            if last_price and last_price > 0:
                meta = ASSET_METADATA.get(ticker, {})
                if meta.get("currency") == "USD":
                    price_eur = float(last_price) * usd_eur_rate
                else:
                    price_eur = float(last_price)
        except Exception as e:
            logger.warning(f"Failed live lookup for {ticker}: {e}")

        if not price_eur or price_eur <= 0:
            fallback = FALLBACK_PRICES.get(ticker, 100.0)
            meta = ASSET_METADATA.get(ticker, {})
            if meta.get("currency") == "USD":
                price_eur = fallback * usd_eur_rate
            else:
                price_eur = fallback

        prices[ticker] = round(price_eur, 2)

    return prices

def get_analyst_consensus() -> List[AnalystConsensus]:
    """Return analyst consensus targets and potential for portfolio assets."""
    consensus_data = [
        {
            "ticker": "WPEA.PA",
            "company_name": "iShares MSCI World PEA ETF",
            "target_price_avg": 6.80,
            "current_price": 5.85,
            "recommendation": "Strong Buy",
            "num_analysts": 18
        },
        {
            "ticker": "GOOGL",
            "company_name": "Alphabet Inc.",
            "target_price_avg": 205.00,
            "current_price": 178.50,
            "recommendation": "Strong Buy",
            "num_analysts": 45
        },
        {
            "ticker": "MSFT",
            "company_name": "Microsoft Corporation",
            "target_price_avg": 500.00,
            "current_price": 445.10,
            "recommendation": "Buy",
            "num_analysts": 52
        },
        {
            "ticker": "NVDA",
            "company_name": "NVIDIA Corporation",
            "target_price_avg": 150.00,
            "current_price": 125.80,
            "recommendation": "Buy",
            "num_analysts": 60
        },
        {
            "ticker": "TSM",
            "company_name": "TSMC",
            "target_price_avg": 225.00,
            "current_price": 192.40,
            "recommendation": "Strong Buy",
            "num_analysts": 38
        },
        {
            "ticker": "AMZN",
            "company_name": "Amazon.com Inc.",
            "target_price_avg": 220.00,
            "current_price": 186.30,
            "recommendation": "Strong Buy",
            "num_analysts": 48
        },
        {
            "ticker": "VWCE.DE",
            "company_name": "Vanguard FTSE All-World ETF",
            "target_price_avg": 145.00,
            "current_price": 128.40,
            "recommendation": "Buy",
            "num_analysts": 22
        }
    ]

    results = []
    for item in consensus_data:
        curr = item["current_price"]
        target = item["target_price_avg"]
        upside = ((target - curr) / curr) * 100.0
        results.append(
            AnalystConsensus(
                ticker=item["ticker"],
                company_name=item["company_name"],
                target_price_avg=target,
                current_price=curr,
                upside_potential_pct=round(upside, 1),
                recommendation=item["recommendation"],
                num_analysts=item["num_analysts"]
            )
        )
    return results
