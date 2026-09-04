"use client";

import React, { useState, useEffect } from "react";
import {
  PeaDcaGuide,
  StructuredProduct,
  ArbitrageRecommendation,
  TaxSimulation,
  fetchPeaDcaGuide,
  fetchStructuredProduct,
  fetchArbitrageRecommendations,
  simulateFlatTax,
} from "@/lib/api";
import {
  Calculator,
  ShieldAlert,
  ArrowRightLeft,
  CheckCircle2,
  DollarSign,
  TrendingUp,
  Percent,
  Sparkles,
  Info,
} from "lucide-react";

export default function AdvisoryCenter() {
  const [dcaAmount, setDcaAmount] = useState<number>(100);
  const [dcaGuide, setDcaGuide] = useState<PeaDcaGuide | null>(null);
  const [structuredProduct, setStructuredProduct] = useState<StructuredProduct | null>(null);
  const [arbitrages, setArbitrages] = useState<ArbitrageRecommendation[]>([]);

  // Flat Tax Interactive Simulator State
  const [simUnits, setSimUnits] = useState<number>(2.0);
  const [simBuyPrice, setSimBuyPrice] = useState<number>(117.36);
  const [simCurrPrice, setSimCurrPrice] = useState<number>(125.8);
  const [simTicker, setSimTicker] = useState<string>("NVDA");
  const [taxResult, setTaxResult] = useState<TaxSimulation | null>(null);

  useEffect(() => {
    loadAdvisoryData();
  }, [dcaAmount]);

  const loadAdvisoryData = async () => {
    try {
      const guide = await fetchPeaDcaGuide(dcaAmount);
      setDcaGuide(guide);

      const sp = await fetchStructuredProduct();
      setStructuredProduct(sp);

      const arbs = await fetchArbitrageRecommendations();
      setArbitrages(arbs);

      runTaxSimulation();
    } catch (err) {
      console.error("Error loading advisory data", err);
    }
  };

  const runTaxSimulation = async () => {
    try {
      const res = await simulateFlatTax(simUnits, simBuyPrice, simCurrPrice, simTicker);
      setTaxResult(res);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    runTaxSimulation();
  }, [simUnits, simBuyPrice, simCurrPrice, simTicker]);

  return (
    <div className="space-y-8">
      {/* 1. FORTUNEO PEA MONTHLY DCA OPTIMIZER */}
      <div className="bg-slate-900 border border-blue-900/50 rounded-xl p-6 shadow-sm space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-4">
          <div>
            <div className="flex items-center space-x-2">
              <Sparkles className="w-5 h-5 text-blue-400" />
              <h2 className="text-lg font-bold text-white">Optimiseur DCA Mensuel — PEA Fortuneo (Offre Starter)</h2>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Maximisez la gratuité de votre 1er ordre du mois (&lt;= 500 €) sur l'ETF MSCI World PEA (WPEA).
            </p>
          </div>

          <div className="flex items-center space-x-3 bg-slate-950 p-2 rounded-lg border border-slate-800">
            <span className="text-xs font-semibold text-slate-300">Versement prévu :</span>
            <input
              type="number"
              min="50"
              max="500"
              step="10"
              value={dcaAmount}
              onChange={(e) => setDcaAmount(Number(e.target.value))}
              className="w-20 bg-slate-900 border border-slate-700 text-white text-xs rounded px-2 py-1 font-bold text-center focus:outline-none focus:border-blue-500"
            />
            <span className="text-xs text-slate-400">€ / mois</span>
          </div>
        </div>

        {dcaGuide && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-slate-950 p-4 rounded-lg border border-slate-800">
              <span className="text-xs text-slate-400">ETF Recommandé</span>
              <p className="text-sm font-bold text-white mt-1">{dcaGuide.recommended_etf_ticker}</p>
              <p className="text-[10px] text-slate-400 truncate">{dcaGuide.recommended_etf_name}</p>
            </div>

            <div className="bg-slate-950 p-4 rounded-lg border border-slate-800">
              <span className="text-xs text-slate-400">Nombre de Parts à Acheter</span>
              <p className="text-xl font-bold text-blue-400 mt-1">{dcaGuide.affordable_units} parts</p>
              <p className="text-[10px] text-slate-400">Prix unitaire : {dcaGuide.etf_price.toFixed(2)} €</p>
            </div>

            <div className="bg-slate-950 p-4 rounded-lg border border-slate-800">
              <span className="text-xs text-slate-400">Coût Total de l'Ordre</span>
              <p className="text-xl font-bold text-emerald-400 mt-1">{dcaGuide.total_order_cost.toFixed(2)} €</p>
              <p className="text-[10px] text-slate-400">Solde restant : {dcaGuide.remaining_cash.toFixed(2)} €</p>
            </div>

            <div className="bg-slate-950 p-4 rounded-lg border border-slate-800">
              <span className="text-xs text-slate-400">Frais de Courtage Fortuneo</span>
              <p className="text-xl font-bold text-emerald-400 mt-1">0,00 €</p>
              <span className="inline-block text-[10px] font-bold text-emerald-400 bg-emerald-950 px-2 py-0.5 rounded border border-emerald-800/40 mt-1">
                Offre Starter (1er ordre gratuit)
              </span>
            </div>
          </div>
        )}
      </div>

      {/* 2. FLAT TAX (30%) SIMULATOR */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm space-y-6">
        <div className="flex items-center space-x-2 border-b border-slate-800 pb-4">
          <Calculator className="w-5 h-5 text-indigo-400" />
          <div>
            <h2 className="text-lg font-bold text-white">Simulateur d'Impact Fiscal (Flat Tax 30%)</h2>
            <p className="text-xs text-slate-400">
              Calculez le montant exact de la Flat Tax (12,8 % IR + 17,2 % PS) avant tout arbitrage sur Goliaths ou Trading 212.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 bg-slate-950 p-4 rounded-xl border border-slate-800">
          <div>
            <label className="text-xs text-slate-400 block mb-1">Actif / Ticker</label>
            <input
              type="text"
              value={simTicker}
              onChange={(e) => setSimTicker(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 text-white text-xs rounded px-3 py-2 font-semibold"
            />
          </div>
          <div>
            <label className="text-xs text-slate-400 block mb-1">Quantité à Vendre</label>
            <input
              type="number"
              step="0.1"
              value={simUnits}
              onChange={(e) => setSimUnits(Number(e.target.value))}
              className="w-full bg-slate-900 border border-slate-700 text-white text-xs rounded px-3 py-2 font-semibold"
            />
          </div>
          <div>
            <label className="text-xs text-slate-400 block mb-1">Prix Moyen d'Achat (€)</label>
            <input
              type="number"
              step="1"
              value={simBuyPrice}
              onChange={(e) => setSimBuyPrice(Number(e.target.value))}
              className="w-full bg-slate-900 border border-slate-700 text-white text-xs rounded px-3 py-2 font-semibold"
            />
          </div>
          <div>
            <label className="text-xs text-slate-400 block mb-1">Prix de Revente Estimé (€)</label>
            <input
              type="number"
              step="1"
              value={simCurrPrice}
              onChange={(e) => setSimCurrPrice(Number(e.target.value))}
              className="w-full bg-slate-900 border border-slate-700 text-white text-xs rounded px-3 py-2 font-semibold"
            />
          </div>
        </div>

        {taxResult && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
            <div className="bg-slate-950 p-3.5 rounded-lg border border-slate-800">
              <span className="text-slate-400">Produit Brut Vente</span>
              <p className="text-base font-bold text-white mt-1">{taxResult.gross_proceeds.toFixed(2)} €</p>
            </div>
            <div className="bg-slate-950 p-3.5 rounded-lg border border-slate-800">
              <span className="text-slate-400">Plus-Value Brute</span>
              <p className={`text-base font-bold mt-1 ${taxResult.gross_gain >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
                {taxResult.gross_gain >= 0 ? "+" : ""}{taxResult.gross_gain.toFixed(2)} €
              </p>
            </div>
            <div className="bg-slate-950 p-3.5 rounded-lg border border-slate-800">
              <span className="text-slate-400">Flat Tax À Payer (30%)</span>
              <p className="text-base font-bold text-rose-400 mt-1">{taxResult.tax_amount.toFixed(2)} €</p>
            </div>
            <div className="bg-slate-950 p-3.5 rounded-lg border border-slate-800">
              <span className="text-slate-400">Capital Net Récupéré</span>
              <p className="text-base font-bold text-blue-400 mt-1">{taxResult.net_proceeds.toFixed(2)} €</p>
            </div>
          </div>
        )}
      </div>

      {/* 3. OIL STRUCTURED PRODUCT PROTECTION BARRIER TRACKER */}
      {structuredProduct && (
        <div className="bg-slate-900 border border-amber-900/50 rounded-xl p-6 shadow-sm space-y-6">
          <div className="flex justify-between items-start border-b border-slate-800 pb-4">
            <div className="flex items-center space-x-2">
              <ShieldAlert className="w-5 h-5 text-amber-400" />
              <div>
                <h2 className="text-lg font-bold text-white">Suivi Produit Structuré Pétrole (Horizon 2030)</h2>
                <p className="text-xs text-slate-400">Barrière de protection en capital fixée à -40 % du cours initial.</p>
              </div>
            </div>
            <span className="text-xs font-bold px-3 py-1 rounded bg-amber-950 text-amber-300 border border-amber-800/60">
              Statut : {structuredProduct.status}
            </span>
          </div>

          <p className="text-xs text-slate-200 bg-amber-950/40 p-3 rounded-lg border border-amber-900/40">
            {structuredProduct.alert_message}
          </p>

          <div className="space-y-3">
            <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
              Sous-jacents du Produit (HAL, VLO, PBR, DVN)
            </h4>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {structuredProduct.underlyings.map((u) => (
                <div key={u.ticker} className="bg-slate-950 p-4 rounded-lg border border-slate-800 space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="font-bold text-white text-sm">{u.ticker}</span>
                    <span
                      className={`text-xs font-bold ${
                        u.price_change_pct >= 0 ? "text-emerald-400" : "text-amber-400"
                      }`}
                    >
                      {u.price_change_pct >= 0 ? "+" : ""}
                      {u.price_change_pct}%
                    </span>
                  </div>
                  <p className="text-[10px] text-slate-400">{u.name}</p>
                  <div className="pt-2 border-t border-slate-800 text-[10px] space-y-1 text-slate-400">
                    <div className="flex justify-between">
                      <span>Cours initial :</span>
                      <span className="text-slate-200">{u.initial_price} $</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Barrière (-40%) :</span>
                      <span className="text-amber-400 font-bold">{u.barrier_price} $</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* 4. STRATEGIC ARBITRAGE RECOMMENDATIONS FOR EXISTING CAPITAL */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm space-y-6">
        <div className="flex items-center space-x-2 border-b border-slate-800 pb-4">
          <ArrowRightLeft className="w-5 h-5 text-emerald-400" />
          <div>
            <h2 className="text-lg font-bold text-white">Moteur de Remaniement & Arbitrages (Horizon 4 ans - 2030)</h2>
            <p className="text-xs text-slate-400">
              Propositions d'optimisation du capital existant sur Goliaths et Trading 212 sans réinjecter d'argent frais.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4">
          {arbitrages.map((arb) => (
            <div key={arb.id} className="bg-slate-950 p-5 rounded-xl border border-slate-800 space-y-3">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-2">
                <div>
                  <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-blue-950 text-blue-400 border border-blue-800/40">
                    {arb.account_name}
                  </span>
                  <h3 className="text-md font-bold text-white mt-1">{arb.title}</h3>
                </div>

                <div className="text-right">
                  <span className="text-xs text-slate-400">Montant Estimé :</span>
                  <p className="text-base font-bold text-emerald-400">{arb.estimated_amount} €</p>
                </div>
              </div>

              <p className="text-xs text-slate-300 leading-relaxed">{arb.rationale}</p>

              <div className="flex flex-wrap items-center justify-between pt-3 border-t border-slate-800 text-xs text-slate-400">
                <span>Action : <strong className="text-slate-200">{arb.action}</strong></span>
                <span>Taxe Est. (Flat Tax 30%) : <strong className="text-rose-400">{arb.estimated_tax} €</strong></span>
                <span>Capital Net : <strong className="text-blue-400">{arb.net_amount_after_tax} €</strong></span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
