from typing import List, Dict
from backend.models import (
    TaxSimulation,
    ArbitrageRecommendation,
    StructuredProduct,
    StructuredProductUnderlying,
    PeaDcaGuide,
    AcademyConcept,
    MarketNewsItem
)

# Initial baseline pricing for oil structured product underlyings (at issuance / entry)
OIL_UNDERLYING_INITIAL = {
    "HAL": {"name": "Halliburton", "initial": 35.00},
    "VLO": {"name": "Valero Energy", "initial": 150.00},
    "PBR": {"name": "Petrobras", "initial": 14.00},
    "DVN": {"name": "Devon Energy", "initial": 45.00}
}

def calculate_flat_tax(sell_units: float, buy_price: float, current_price: float, ticker: str = "ASSET") -> TaxSimulation:
    """Calculates French Flat Tax (30% PFU) on realized capital gains."""
    gross_proceeds = round(sell_units * current_price, 2)
    cost_basis = sell_units * buy_price
    gross_gain = round(gross_proceeds - cost_basis, 2)

    # Flat tax applies only to positive capital gains
    if gross_gain > 0:
        tax_amount = round(gross_gain * 0.30, 2)
    else:
        tax_amount = 0.0

    net_gain = round(gross_gain - tax_amount, 2)
    net_proceeds = round(gross_proceeds - tax_amount, 2)

    return TaxSimulation(
        ticker=ticker,
        sell_units=sell_units,
        buy_price=buy_price,
        current_price=current_price,
        gross_proceeds=gross_proceeds,
        gross_gain=gross_gain,
        flat_tax_rate=0.30,
        tax_amount=tax_amount,
        net_gain=net_gain,
        net_proceeds=net_proceeds
    )

def evaluate_structured_product(current_prices: Dict[str, float]) -> StructuredProduct:
    """Evaluates the status of the Oil Structured Product against its -40% protection barrier."""
    underlyings = []
    worst_pct = 0.0

    for ticker, info in OIL_UNDERLYING_INITIAL.items():
        curr = current_prices.get(ticker, info["initial"])
        init = info["initial"]
        change_pct = round(((curr - init) / init) * 100.0, 2)
        barrier_price = round(init * 0.60, 2)  # -40% threshold
        distance_pct = round(change_pct - (-40.0), 2)
        is_breached = change_pct <= -40.0

        if change_pct < worst_pct or len(underlyings) == 0:
            worst_pct = change_pct

        underlyings.append(
            StructuredProductUnderlying(
                ticker=ticker,
                name=info["name"],
                initial_price=init,
                current_price=curr,
                price_change_pct=change_pct,
                barrier_price=barrier_price,
                distance_to_barrier_pct=distance_pct,
                is_barrier_breached=is_breached
            )
        )

    # Status classification
    if worst_pct <= -40.0:
        status = "BREACHED"
        msg = "⚠️ ALERTE : La barrière de protection (-40 %) a été franchie par l'une des sous-jacentes. Risque de perte en capital à l'échéance."
    elif worst_pct <= -25.0:
        status = "WARNING"
        msg = "⚡ ATTENTION : Le sous-jacent le plus faible approche de la barrière de protection (-40 %). À surveiller de près jusqu'en mars 2030."
    else:
        status = "SECURE"
        msg = "✅ SÉCURISÉ : Le produit structuré est au-dessus de sa barrière de protection (-40 %). Échéance fixée au 15/03/2030."

    return StructuredProduct(
        name="Produit Structuré Pétrole 2030",
        invested_amount=493.02,
        current_value=493.02 * (1.0 + worst_pct / 100.0 if worst_pct < 0 else 1.05),
        maturity_date="2030-03-15",
        protection_barrier_pct=-40.0,
        underlyings=underlyings,
        worst_underlying_pct=worst_pct,
        status=status,
        alert_message=msg
    )

def generate_pea_dca_guide(pea_cash: float = 100.0, monthly_deposit: float = 100.0, wpea_price: float = 5.85) -> PeaDcaGuide:
    """Generates monthly DCA recommendations for PEA Fortuneo Starter offer."""
    total_available = pea_cash + monthly_deposit
    affordable_units = int(total_available // wpea_price)
    total_cost = round(affordable_units * wpea_price, 2)
    remaining_cash = round(total_available - total_cost, 2)

    # Offre Starter Fortuneo : 1er ordre du mois <= 500€ est 100% gratuit
    is_fee_free = total_cost <= 500.0
    fortuneo_fee = 0.0 if is_fee_free else max(1.95, round(total_cost * 0.0035, 2))

    summary = (
        f"Acheter {affordable_units} parts de l'ETF MSCI World PEA (WPEA) pour un total de {total_cost:.2f} €. "
        f"Grâce à l'offre Starter Fortuneo, votre 1er ordre du mois (< 500 €) bénéficie de 0 € de frais de courtage."
    )

    return PeaDcaGuide(
        monthly_deposit=monthly_deposit,
        recommended_etf_ticker="WPEA.PA",
        recommended_etf_name="iShares MSCI World Swap PEA UCITS ETF",
        etf_price=wpea_price,
        affordable_units=affordable_units,
        total_order_cost=total_cost,
        remaining_cash=remaining_cash,
        fortuneo_fee=fortuneo_fee,
        is_fee_free=is_fee_free,
        next_action_date="1er du mois prochain",
        recommendation_summary=summary
    )

def generate_arbitrage_recommendations(goliaths_value: float, t212_value: float) -> List[ArbitrageRecommendation]:
    """Provides strategic 4-year horizon (2026-2030) arbitrage options for existing inactive accounts."""
    return [
        ArbitrageRecommendation(
            id="arb-goliaths-1",
            account_id="goliaths",
            account_name="Compte Goliaths (CTO Inactif)",
            action="REBALANCE",
            from_ticker="AMZN / KO / MSFT / TSM",
            to_ticker="WPEA.PA / PEA Fortuneo",
            units=None,
            estimated_amount=round(goliaths_value * 0.40, 2),
            estimated_tax=round(goliaths_value * 0.40 * 0.05, 2), # Minimal gain tax estimation
            net_amount_after_tax=round(goliaths_value * 0.40 * 0.95, 2),
            horizon_years=4,
            title="Consolidation des Micro-Lignes Goliaths vers le PEA",
            rationale="Les micro-positions sur Goliaths (KO ~11€, TSM ~10€, MSFT ~10€) sont très éparpillées. Les arbitrer progressivement vers l'ETF MSCI World PEA permet de supprimer les frais de gestion dormants et de bénéficier d'une exonération fiscale d'impôt sur le revenu après 5 ans sur le PEA.",
            risk_impact="LOWER_RISK"
        ),
        ArbitrageRecommendation(
            id="arb-t212-1",
            account_id="trading212",
            account_name="Compte Trading 212 (CTO Inactif)",
            action="HOLD_AND_HARVEST",
            from_ticker="NVDA",
            to_ticker="VWCE.DE / WPEA.PA",
            units=1.5,
            estimated_amount=234.72,
            estimated_tax=18.50,
            net_amount_after_tax=216.22,
            horizon_years=4,
            title="Prise de bénéfices partielle sur NVIDIA",
            rationale="NVIDIA représente une part significative (~22 %) du compte Trading 212. Vendre partiellement après Flat Tax (30 %) permet de sécuriser les plus-values exceptionnelles et de réallouer vers l'ETF Monde (VWCE/WPEA) pour lisser la volatilité d'ici 2030.",
            risk_impact="OPTIMIZE_YIELD"
        ),
        ArbitrageRecommendation(
            id="arb-goliaths-oil",
            account_id="goliaths",
            account_name="Compte Goliaths (CTO Inactif)",
            action="HOLD",
            from_ticker="Produit Structuré Pétrole",
            to_ticker="Échéance 15/03/2030",
            units=1.0,
            estimated_amount=493.02,
            estimated_tax=0.0,
            net_amount_after_tax=493.02,
            horizon_years=4,
            title="Maintien du Produit Structuré Pétrole jusqu'en 2030",
            rationale="Le produit structuré dispose d'une barrière de protection à -40 %. Conserver la position jusqu'à l'échéance du 15/03/2030 afin de bénéficier du mécanisme de remboursement du capital et du coupon prévu, sans nouvel apport.",
            risk_impact="STREAMLINE"
        )
    ]

def get_academy_concepts() -> List[AcademyConcept]:
    """Returns educational financial concepts designed for beginners."""
    return [
        AcademyConcept(
            id="dca",
            title="DCA (Dollar-Cost Averaging) / Versement Programmé",
            short_definition="Technique d'investissement consistant à verser un montant fixe à intervalle régulier (ex: 100€/mois), quel que soit l'état du marché.",
            detailed_explanation="Le DCA élimine la tentation émotionnelle d'essayer de 'deviner le bon moment' (Market Timing). Quand le marché baisse, vous achetez plus de parts à bas prix. Quand le marché monte, vous achetez moins de parts mais vos parts existantes prennent de la valeur. Sur 15-20 ans, cette méthode lisse le prix moyen d'achat et réduit considérablement le risque.",
            concrete_example="Investir 100 € chaque 1er du mois sur l'ETF MSCI World PEA sur Fortuneo Starter.",
            category="Stratégie",
            key_takeaway="La régularité bat le timing de marché sur le long terme."
        ),
        AcademyConcept(
            id="etf",
            title="ETF (Exchange-Traded Fund) / Fonds Indiciel",
            short_definition="Un fonds coté en bourse qui réplique la performance d'un panier de centaines ou milliers d'entreprises en un seul achat.",
            detailed_explanation="Plutôt que d'acheter une seule action et de prendre le risque de faillite de cette entreprise, un ETF MSCI World vous permet d'investir simultanément dans plus de 1 400 entreprises leaders mondiales (Apple, Microsoft, Nestlé, Toyota...). Les frais de gestion sont extrêmement faibles (environ 0,20 %/an contre 2 % pour un fonds traditionnel).",
            concrete_example="L'ETF iShares MSCI World PEA (WPEA) réplique l'économie mondiale depuis un PEA français.",
            category="Produits",
            key_takeaway="Diversification maximale à frais réduits."
        ),
        AcademyConcept(
            id="flat-tax",
            title="Flat Tax / Prélèvement Forfaitaire Unique (PFU) à 30 %",
            short_definition="Régime fiscal français appliquant une taxe globale de 30 % sur les plus-values et dividendes en Compte Titres Ordinaire (CTO).",
            detailed_explanation="La Flat Tax se décompose en 12,8 % d'impôt sur le revenu et 17,2 % de prélèvements sociaux. Elle est appliquée uniquement sur la plus-value réalisée lors de la revente (pas sur le capital initial). En comparaison, le PEA permet une exonération totale d'impôt sur le revenu après 5 ans de détention (seuls les 17,2 % de prélèvements sociaux restent dus).",
            concrete_example="Si vous vendez une action avec 100 € de plus-value sur Trading 212, vous payez 30 € de Flat Tax et conservez 70 € de gain net.",
            category="Fiscalité",
            key_takeaway="Privilégier le PEA pour éviter les 12,8 % d'impôt sur les gains."
        ),
        AcademyConcept(
            id="drawdown",
            title="Repli de marché / Drawdown & Volatilité",
            short_definition="Baisse temporaire de la valeur d'un portefeuille par rapport à son point le plus haut historique.",
            detailed_explanation="En bourse long terme (15-20 ans), des baisses de -10 %, -20 % voire -30 % surviennent régulièrement (crises géopolitiques, récessions). Un investisseur débutant doit comprendre que ces replis sont normaux et temporaires. Historiquement, le marché mondial s'est toujours relevé et a atteint de nouveaux sommets.",
            concrete_example="Pendant la crise du COVID-19 en 2020, le MSCI World a chuté d'environ 30 % avant de rebondir fortement les mois suivants.",
            category="Risques",
            key_takeaway="Ne pas vendre lors des baisses : c'est au contraire une opportunité d'achat à prix réduit."
        ),
        AcademyConcept(
            id="leverage",
            title="Effet de Levier (Leverage)",
            short_definition="Mécanisme financier permettant d'amplifier les gains (et les pertes) en empruntant des capitaux.",
            detailed_explanation="L'effet de levier peut multiplier la rentabilité quand le marché monte, mais il accélère la perte du capital en cas de baisse et peut mener à la ruine en cas de décalage violent. Pour un investisseur long terme débutant, il est très fortement déconseillé d'utiliser du levier en CTO.",
            concrete_example="Un ETF à levier x2 qui subit une baisse du marché de 50 % voit sa valeur s'effondrer à zéro.",
            category="Risques",
            key_takeaway="À éviter en stratégie d'investissement patrimoniale long terme."
        ),
        AcademyConcept(
            id="arbitrage",
            title="Arbitrage de Portefeuille",
            short_definition="Action de vendre un actif moins performant ou trop risqué pour racheter un actif mieux aligné avec ses objectifs.",
            detailed_explanation="L'arbitrage permet de nettoyer les micro-lignes éparpillées ou surpondérées sans réinjecter d'argent frais. Avant tout arbitrage sur CTO, il faut impérativement calculer le coût de la Flat Tax à régler.",
            concrete_example="Vendre la ligne NVIDIA sur Trading 212 pour renforcer l'ETF MSCI World sur PEA.",
            category="Stratégie",
            key_takeaway="Réallouer intelligemment le capital existant après impact fiscal."
        )
    ]

def get_market_news() -> List[MarketNewsItem]:
    """Returns curated geopolitical & financial news items relevant to the portfolio."""
    return [
        MarketNewsItem(
            id="news-1",
            title="Politiques monétaires & Taux des banques centrales (BCE & Fed)",
            source="Financial Times / Bloomberg",
            url="https://finance.yahoo.com",
            published_at="Aujourd'hui",
            summary="Les banques centrales poursuivent leur assouplissement monétaire progressif, ce qui soutient les valorisations des marchés actions mondiaux et des grandes capitalisations technologiques.",
            geopolitical_impact="Facteur favorable à long terme pour les ETF MSCI World et les géants de la Tech (MSFT, GOOGL, NVDA).",
            impact_level="MEDIUM",
            relevant_tickers=["WPEA.PA", "VWCE.DE", "MSFT", "GOOGL"]
        ),
        MarketNewsItem(
            id="news-2",
            title="Tensions géopolitiques au Moyen-Orient & Volatilité du pétrole",
            source="Reuters",
            url="https://finance.yahoo.com",
            published_at="Hiere",
            summary="Les fluctuations des cours du baril de pétrole créent de la volatilité sur les valeurs énergétiques et para-pétrolières. L'impact reste surveillé pour le produit structuré Goliaths.",
            geopolitical_impact="Surveillance renforcée des sous-jacents pétroliers (HAL, VLO, PBR, DVN). La barrière à -40% reste largement préservée.",
            impact_level="HIGH",
            relevant_tickers=["HAL", "VLO", "PBR", "DVN"]
        ),
        MarketNewsItem(
            id="news-3",
            title="Investissements massifs dans les infrastructures d'Intelligence Artificielle",
            source="Les Échos / Wall Street Journal",
            url="https://finance.yahoo.com",
            published_at="Cette semaine",
            summary="Les dépenses en capital (CapEx) des Big Tech (Microsoft, Google, Amazon) atteignent des niveaux record pour construire des datacenters IA, profitant directement à TSMC et Nvidia.",
            geopolitical_impact="Excellente visibilité fondamentale sur 3-5 ans pour le secteur des semi-conducteurs et du cloud.",
            impact_level="HIGH",
            relevant_tickers=["NVDA", "TSM", "MSFT", "GOOGL", "AMZN"]
        )
    ]
