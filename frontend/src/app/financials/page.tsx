'use client';

import React, { useState, useEffect } from 'react';
import {
  DollarSign,
  TrendingUp,
  Calculator,
  PieChart,
  Percent,
  CreditCard,
  Building2,
  PackageCheck
} from 'lucide-react';
import api from '@/lib/api';

export default function FinancialsPage() {
  const [products, setProducts] = useState<any[]>([]);
  const [selectedProductId, setSelectedProductId] = useState<number>(0);

  // Financial Sliders State
  const [sellingPrice, setSellingPrice] = useState<number>(44.99);
  const [cogs, setCogs] = useState<number>(8.50);
  const [transport, setTransport] = useState<number>(3.80);
  const [cac, setCac] = useState<number>(12.00);

  const [stripeRate, setStripeRate] = useState<number>(0.015); // 1.5%
  const [stripeFixed, setStripeFixed] = useState<number>(0.25); // 0.25€
  const [socialRate, setSocialRate] = useState<number>(0.123); // 12.3%

  const [calculated, setCalculated] = useState<any>(null);

  useEffect(() => {
    api.get('/api/products').then((res) => {
      setProducts(res.data);
      if (res.data.length > 0) {
        setSelectedProductId(res.data[0].id);
        const p = res.data[0];
        setSellingPrice(p.selling_price || 44.99);
        setCogs(p.estimated_cogs || 8.5);
        setTransport(p.estimated_shipping || 3.8);
        setCac(p.estimated_cac || 12.0);
      }
    });
  }, []);

  const handleProductSelect = (id: number) => {
    setSelectedProductId(id);
    const p = products.find((item) => item.id === id);
    if (p) {
      setSellingPrice(p.selling_price);
      setCogs(p.estimated_cogs);
      setTransport(p.estimated_shipping);
      setCac(p.estimated_cac);
    }
  };

  // Real-time calculation effect
  useEffect(() => {
    const fetchCalculation = async () => {
      try {
        const res = await api.post('/api/financials/calculate', {
          selling_price: sellingPrice,
          cogs: cogs,
          transport_customs: transport,
          cac_ads: cac,
          stripe_fee_rate: stripeRate,
          stripe_fee_fixed: stripeFixed,
          social_contributions_rate: socialRate,
        });
        setCalculated(res.data);
      } catch (err) {
        console.error('Calculation error:', err);
      }
    };

    fetchCalculation();
  }, [sellingPrice, cogs, transport, cac, stripeRate, stripeFixed, socialRate]);

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <div>
          <div className="flex items-center space-x-2 text-emerald-600 font-semibold text-sm mb-1">
            <DollarSign className="w-4 h-4" />
            <span>Module 7 • Dashboard Financier & Rentabilité</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-900">Calculateur de Marge Nette en Temps Réel</h1>
          <p className="text-sm text-slate-500 mt-1">
            Formule : Marge Nette = Prix Vente - (COGS + Transport/Douane + CAC/Pub + Stripe/PayPal + Cotisations Sociales 12.3%)
          </p>
        </div>

        {/* Product selector */}
        {products.length > 0 && (
          <div className="flex items-center space-x-2">
            <label className="text-xs font-semibold text-slate-600 whitespace-nowrap">Charger Produit :</label>
            <select
              value={selectedProductId}
              onChange={(e) => handleProductSelect(parseInt(e.target.value))}
              className="px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-emerald-500"
            >
              {products.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.title}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Sliders Input Panel */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-6">
          <h2 className="text-lg font-bold text-slate-900 flex items-center space-x-2 border-b pb-4">
            <Calculator className="w-5 h-5 text-emerald-600" />
            <span>Variables Financières (€)</span>
          </h2>

          <div className="space-y-5">
            {/* Selling Price */}
            <div>
              <div className="flex justify-between text-xs font-semibold mb-1">
                <span className="text-slate-700">Prix de Vente Client TTC</span>
                <span className="text-emerald-600 font-bold">{sellingPrice.toFixed(2)} €</span>
              </div>
              <input
                type="range"
                min="5"
                max="200"
                step="0.5"
                value={sellingPrice}
                onChange={(e) => setSellingPrice(parseFloat(e.target.value))}
                className="w-full accent-emerald-600 cursor-pointer"
              />
            </div>

            {/* COGS */}
            <div>
              <div className="flex justify-between text-xs font-semibold mb-1">
                <span className="text-slate-700">Prix d'Achat Produit (COGS)</span>
                <span className="text-slate-900">{cogs.toFixed(2)} €</span>
              </div>
              <input
                type="range"
                min="1"
                max="100"
                step="0.1"
                value={cogs}
                onChange={(e) => setCogs(parseFloat(e.target.value))}
                className="w-full accent-emerald-600 cursor-pointer"
              />
            </div>

            {/* Transport & Customs */}
            <div>
              <div className="flex justify-between text-xs font-semibold mb-1">
                <span className="text-slate-700">Transport & Frais de Douane</span>
                <span className="text-slate-900">{transport.toFixed(2)} €</span>
              </div>
              <input
                type="range"
                min="0"
                max="30"
                step="0.1"
                value={transport}
                onChange={(e) => setTransport(parseFloat(e.target.value))}
                className="w-full accent-emerald-600 cursor-pointer"
              />
            </div>

            {/* CAC / Pubs */}
            <div>
              <div className="flex justify-between text-xs font-semibold mb-1">
                <span className="text-slate-700">Coût d'Acquisition Client (CAC Pub)</span>
                <span className="text-slate-900">{cac.toFixed(2)} €</span>
              </div>
              <input
                type="range"
                min="0"
                max="60"
                step="0.5"
                value={cac}
                onChange={(e) => setCac(parseFloat(e.target.value))}
                className="w-full accent-emerald-600 cursor-pointer"
              />
            </div>

            {/* Rates Overview */}
            <div className="p-4 bg-slate-50 rounded-xl space-y-2 border border-slate-200 text-xs">
              <div className="flex justify-between text-slate-600">
                <span>Cotisations Sociales (Micro-entreprise)</span>
                <span className="font-bold text-slate-900">12.3 %</span>
              </div>
              <div className="flex justify-between text-slate-600">
                <span>Frais Stripe / PayPal</span>
                <span className="font-bold text-slate-900">1.5% + 0.25 €</span>
              </div>
            </div>
          </div>
        </div>

        {/* Realtime KPI Results */}
        {calculated && (
          <div className="lg:col-span-2 space-y-6">
            {/* Top Key KPIs */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="bg-slate-900 text-white p-6 rounded-2xl shadow-lg space-y-2">
                <span className="text-xs font-semibold text-emerald-400 uppercase tracking-wider block">
                  Marge Nette (€)
                </span>
                <span className="text-3xl font-black">{calculated.net_margin_euro} €</span>
                <p className="text-xs text-slate-400">Bénéfice net dans votre poche par vente</p>
              </div>

              <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-2">
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block">
                  Marge Nette (%)
                </span>
                <span className="text-3xl font-black text-emerald-600">
                  {calculated.net_margin_percent} %
                </span>
                <p className="text-xs text-slate-500">Pourcentage de rentabilité nette</p>
              </div>

              <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-2">
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block">
                  Total Coûts Opérationnels
                </span>
                <span className="text-3xl font-black text-rose-500">{calculated.total_costs} €</span>
                <p className="text-xs text-slate-500">COGS + Pub + Transport + Taxes</p>
              </div>
            </div>

            {/* Detailed Cost Breakdown */}
            <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
              <h3 className="text-base font-bold text-slate-900 border-b pb-3">
                Ventilation Détaillée des Coûts
              </h3>

              <div className="space-y-3 text-sm">
                <div className="flex justify-between items-center p-3 bg-slate-50 rounded-xl">
                  <span className="text-slate-700 font-medium">Prix Vente Bruta (100%)</span>
                  <span className="font-extrabold text-slate-900">{calculated.selling_price} €</span>
                </div>

                <div className="flex justify-between items-center p-3 bg-slate-50/70 rounded-xl text-xs">
                  <span className="text-slate-600">1. Produit / Achat (COGS)</span>
                  <span className="font-semibold text-slate-800">-{calculated.cogs} €</span>
                </div>

                <div className="flex justify-between items-center p-3 bg-slate-50/70 rounded-xl text-xs">
                  <span className="text-slate-600">2. Transport & Frais Douaniers</span>
                  <span className="font-semibold text-slate-800">-{calculated.transport_customs} €</span>
                </div>

                <div className="flex justify-between items-center p-3 bg-slate-50/70 rounded-xl text-xs">
                  <span className="text-slate-600">3. Coût d'Acquisition Pub (CAC)</span>
                  <span className="font-semibold text-slate-800">-{calculated.cac_ads} €</span>
                </div>

                <div className="flex justify-between items-center p-3 bg-slate-50/70 rounded-xl text-xs">
                  <span className="text-slate-600">4. Frais de Paiement Stripe / PayPal</span>
                  <span className="font-semibold text-slate-800">-{calculated.stripe_fee} €</span>
                </div>

                <div className="flex justify-between items-center p-3 bg-slate-50/70 rounded-xl text-xs">
                  <span className="text-slate-600">5. Cotisations Sociales URSSAF (12.3%)</span>
                  <span className="font-semibold text-slate-800">-{calculated.social_contributions} €</span>
                </div>

                <div className="flex justify-between items-center p-4 bg-emerald-50 text-emerald-800 font-bold rounded-xl border border-emerald-200">
                  <span>Marge Nette Finale Restante</span>
                  <span className="text-lg">={calculated.net_margin_euro} €</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
