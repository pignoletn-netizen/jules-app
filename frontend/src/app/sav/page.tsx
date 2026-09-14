'use client';

import React, { useState, useEffect } from 'react';
import {
  MessageSquare,
  Sparkles,
  Mail,
  Copy,
  Check,
  History,
  Send
} from 'lucide-react';
import api from '@/lib/api';
import LoadingSpinner, { SkeletonCard } from '@/components/LoadingSpinner';

export default function SavPage() {
  const [products, setProducts] = useState<any[]>([]);
  const [selectedProductId, setSelectedProductId] = useState<number>(0);
  const [inquiryType, setInquiryType] = useState('Shipping');
  const [customerEmail, setCustomerEmail] = useState('');
  const [incomingMessage, setIncomingMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [reply, setReply] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const [history, setHistory] = useState<any[]>([]);

  useEffect(() => {
    api.get('/api/products').then((res) => {
      setProducts(res.data);
      if (res.data.length > 0) {
        setSelectedProductId(res.data[0].id);
      }
    });
  }, []);

  const fetchHistory = async (pId: number) => {
    if (!pId) return;
    try {
      const res = await api.get(`/api/sav/history/${pId}`);
      setHistory(res.data);
    } catch (err) {
      console.error('History fetch error:', err);
    }
  };

  useEffect(() => {
    if (selectedProductId) {
      fetchHistory(selectedProductId);
    }
  }, [selectedProductId]);

  const handleGenerateReply = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedProductId || !incomingMessage) return;
    setLoading(true);
    setReply(null);

    try {
      const res = await api.post('/api/sav/generate', {
        product_id: selectedProductId,
        inquiry_type: inquiryType,
        customer_email: customerEmail,
        incoming_message: incomingMessage,
      });
      setReply(res.data.generated_reply);
      fetchHistory(selectedProductId);
    } catch (err: any) {
      console.error('SAV error:', err);
    } finally {
      setLoading(false);
    }
  };

  const copyReply = () => {
    if (!reply) return;
    navigator.clipboard.writeText(reply);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <div>
          <div className="flex items-center space-x-2 text-emerald-600 font-semibold text-sm mb-1">
            <MessageSquare className="w-4 h-4" />
            <span>Module 6 • SAV & Gestion Client Automatisée</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-900">Générateur de Réponses Automatiques IA</h1>
          <p className="text-sm text-slate-500 mt-1">
            Générez instantanément des réponses e-mails professionnelles pour le suivi de colis, retours et remboursements.
          </p>
        </div>

        {/* Product selector */}
        <div className="flex items-center space-x-2">
          <label className="text-xs font-semibold text-slate-600 whitespace-nowrap">Produit :</label>
          <select
            value={selectedProductId}
            onChange={(e) => setSelectedProductId(parseInt(e.target.value))}
            className="px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-emerald-500"
          >
            {products.map((p) => (
              <option key={p.id} value={p.id}>
                {p.title}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left Form */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-5">
          <h2 className="text-lg font-bold text-slate-900 flex items-center space-x-2 border-b pb-4">
            <Mail className="w-5 h-5 text-emerald-600" />
            <span>Nouveau Message Client</span>
          </h2>

          <form onSubmit={handleGenerateReply} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Motif de la Demande</label>
                <select
                  value={inquiryType}
                  onChange={(e) => setInquiryType(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm"
                >
                  <option value="Shipping">Suivi de livraison / Colis non reçu</option>
                  <option value="Return">Demande de retour produit</option>
                  <option value="Refund">Demande de remboursement</option>
                  <option value="Question">Question technique sur le produit</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">E-mail Client (Optionnel)</label>
                <input
                  type="email"
                  value={customerEmail}
                  onChange={(e) => setCustomerEmail(e.target.value)}
                  placeholder="client@exemple.com"
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Message Reçu du Client</label>
              <textarea
                rows={4}
                required
                value={incomingMessage}
                onChange={(e) => setIncomingMessage(e.target.value)}
                placeholder="Ex: Bonjour, j'ai commandé il y a 3 jours et je n'ai toujours pas reçu mon numéro de suivi. Pouvez-vous m'aider ?"
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-emerald-500 focus:outline-none"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl text-sm transition shadow flex items-center justify-center space-x-2"
            >
              {loading ? (
                <span>Rédaction de la réponse par l'IA...</span>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  <span>Générer la Réponse Automatique</span>
                </>
              )}
            </button>
          </form>

          {/* Generated Answer Display */}
          {reply && (
            <div className="pt-4 border-t border-slate-100 space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-xs font-bold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-lg">
                  Réponse Recommandée
                </span>
                <button
                  onClick={copyReply}
                  className="flex items-center space-x-1 text-xs text-slate-600 hover:text-slate-900 bg-slate-100 px-3 py-1 rounded-lg"
                >
                  {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{copied ? 'Copié !' : 'Copier'}</span>
                </button>
              </div>

              <div className="p-4 bg-slate-900 text-slate-100 rounded-xl text-xs leading-relaxed whitespace-pre-line font-mono">
                {reply}
              </div>
            </div>
          )}
        </div>

        {/* Right History */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-6">
          <div className="border-b pb-4 flex items-center justify-between">
            <h2 className="text-lg font-bold text-slate-900 flex items-center space-x-2">
              <History className="w-5 h-5 text-emerald-600" />
              <span>Historique Réponses SAV ({history.length})</span>
            </h2>
          </div>

          {history.length === 0 ? (
            <div className="text-center py-12 text-slate-400 text-sm">
              <span>Aucune réponse SAV enregistrée pour ce produit.</span>
            </div>
          ) : (
            <div className="space-y-4 max-h-[500px] overflow-y-auto pr-1">
              {history.map((item) => (
                <div key={item.id} className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-2 text-xs">
                  <div className="flex justify-between items-center text-slate-500 font-semibold">
                    <span>{item.inquiry_type}</span>
                    <span>{new Date(item.created_at).toLocaleDateString('fr-FR')}</span>
                  </div>

                  <div className="text-slate-800 italic bg-white p-2.5 rounded border border-slate-100">
                    "{item.incoming_message}"
                  </div>

                  <div className="text-slate-600 whitespace-pre-line font-mono text-[11px] pt-1">
                    {item.generated_reply}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
