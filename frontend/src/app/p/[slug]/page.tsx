'use client';

import React, { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { Sparkles, CheckCircle, ShieldCheck, Truck, ArrowRight, Heart } from 'lucide-react';
import api from '@/lib/api';

export default function PublicLandingPage() {
  const params = useParams();
  const slug = params?.slug as string;

  const [landing, setLanding] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [clicked, setClicked] = useState(false);

  useEffect(() => {
    if (!slug) return;
    api.get(`/api/landing-pages/public/${slug}`)
      .then((res) => setLanding(res.data))
      .catch((err) => console.error('Landing fetch error:', err))
      .finally(() => setLoading(false));
  }, [slug]);

  const handleCtaClick = () => {
    setClicked(true);
    api.post(`/api/landing-pages/public/${slug}/intent`, { action_type: 'click' })
      .catch((err) => console.error(err));
  };

  const handleEmailSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;
    api.post(`/api/landing-pages/public/${slug}/intent`, {
      action_type: 'email_signup',
      email: email,
    }).then(() => {
      setSubmitted(true);
    }).catch((err) => console.error(err));
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="w-10 h-10 border-4 border-emerald-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!landing) {
    return (
      <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center p-6 text-center">
        <h1 className="text-2xl font-bold text-slate-800">Landing Page Introuvable</h1>
        <p className="text-sm text-slate-500 mt-2">Le produit demandé n'existe pas ou la page a été déplacée.</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 font-sans">
      {/* Top Banner */}
      <div className="bg-emerald-600 text-slate-950 font-bold text-center py-2 text-xs uppercase tracking-wider">
        🔥 Offre Spéciale Lancement - Réduction Exclusive Immédiate
      </div>

      {/* Hero Section */}
      <header className="max-w-4xl mx-auto px-6 py-16 text-center space-y-6">
        <div className="inline-flex items-center space-x-2 px-4 py-1.5 bg-emerald-500/10 border border-emerald-500/30 rounded-full text-emerald-400 text-xs font-semibold">
          <Sparkles className="w-4 h-4" />
          <span>Produit d'Innovation 2026</span>
        </div>

        <h1 className="text-3xl md:text-5xl font-extrabold text-white leading-tight">
          {landing.main_headline}
        </h1>

        <p className="text-base md:text-xl text-slate-300 max-w-2xl mx-auto leading-relaxed">
          {landing.subheadline}
        </p>

        {/* Call to Action Button */}
        <div className="pt-4 flex flex-col items-center space-y-3">
          <button
            onClick={handleCtaClick}
            className="w-full sm:w-auto px-8 py-4 bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-lg font-extrabold rounded-2xl shadow-xl shadow-emerald-500/20 transform hover:-translate-y-0.5 transition flex items-center justify-center space-x-3"
          >
            <span>{landing.call_to_action || 'Commander Maintenant'}</span>
            <ArrowRight className="w-5 h-5" />
          </button>
          {clicked && (
            <span className="text-xs text-emerald-400 font-medium animate-pulse">
              ✓ Intention d'achat enregistrée avec succès !
            </span>
          )}
        </div>
      </header>

      {/* Selling Points */}
      <section className="bg-slate-800/80 border-y border-slate-700 py-12">
        <div className="max-w-3xl mx-auto px-6 space-y-4">
          <h2 className="text-xl font-bold text-white text-center mb-6">
            Pourquoi Choisir Notre Solution ?
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {landing.selling_points?.map((sp: string, i: number) => (
              <div key={i} className="flex items-start space-x-3 p-4 bg-slate-900/60 rounded-xl border border-slate-700/50">
                <CheckCircle className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
                <span className="text-sm text-slate-200">{sp}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Email VIP Reservation Form */}
      <section className="max-w-2xl mx-auto px-6 py-16 text-center space-y-6">
        <div className="p-8 bg-slate-800 border border-slate-700 rounded-3xl space-y-4 shadow-2xl">
          <Heart className="w-8 h-8 text-rose-500 mx-auto" />
          <h3 className="text-2xl font-bold text-white">Réservation VIP & Accès Prioritaire</h3>
          <p className="text-xs text-slate-400">
            Inscrivez votre e-mail pour recevoir le code promo exclusif (-40%) lors de l'ouverture officielle des stocks.
          </p>

          {submitted ? (
            <div className="p-4 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 rounded-xl font-semibold text-sm">
              🎉 Félicitations ! Votre e-mail a été enregistré. Vous serez le premier informé !
            </div>
          ) : (
            <form onSubmit={handleEmailSubmit} className="flex flex-col sm:flex-row gap-3">
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Entrez votre e-mail..."
                className="flex-1 px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white placeholder-slate-500 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
              <button
                type="submit"
                className="px-6 py-3 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold rounded-xl text-sm transition"
              >
                Réserver mon Offre
              </button>
            </form>
          )}
        </div>
      </section>

      {/* FAQ */}
      {landing.faq_list && landing.faq_list.length > 0 && (
        <section className="max-w-3xl mx-auto px-6 pb-16 space-y-6">
          <h3 className="text-xl font-bold text-white text-center">Foire Aux Questions (FAQ)</h3>
          <div className="space-y-3">
            {landing.faq_list.map((faq: any, idx: number) => (
              <div key={idx} className="p-5 bg-slate-800/50 border border-slate-700 rounded-2xl space-y-1">
                <p className="font-semibold text-emerald-400 text-sm">{faq.question}</p>
                <p className="text-xs text-slate-300">{faq.answer}</p>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Footer */}
      <footer className="border-t border-slate-800 py-6 text-center text-xs text-slate-500">
        © 2026 Marque MVB Démo. Tous droits réservés.
      </footer>
    </div>
  );
}
