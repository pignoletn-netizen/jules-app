'use client';

import React, { useState, useEffect } from 'react';
import {
  Truck,
  Plus,
  CheckCircle,
  XCircle,
  Clock,
  Package,
  DollarSign,
  Building,
  ShieldCheck,
  X
} from 'lucide-react';
import api from '@/lib/api';
import LoadingSpinner, { SkeletonCard } from '@/components/LoadingSpinner';

export default function SuppliersPage() {
  const [suppliers, setSuppliers] = useState<any[]>([]);
  const [products, setProducts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [selectedProductId, setSelectedProductId] = useState<string>('');
  const [reliableOnly, setReliableOnly] = useState(false);

  const [formData, setFormData] = useState({
    name: '',
    platform: 'Alibaba',
    years_in_business: 4,
    is_verified: true,
    response_rate: 95.0,
    unit_price: 6.5,
    min_order_quantity: 100,
    shipping_cost: 2.5,
    lead_time_days: 12,
    customization_cost: 0.5,
    product_id: 0,
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const [prodRes, supRes] = await Promise.all([
        api.get('/api/products'),
        api.get(`/api/suppliers${reliableOnly ? '?reliable_only=true' : ''}`),
      ]);
      setProducts(prodRes.data);
      setSuppliers(supRes.data);
      if (prodRes.data.length > 0 && formData.product_id === 0) {
        setFormData((prev) => ({ ...prev, product_id: prodRes.data[0].id }));
      }
    } catch (err) {
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [reliableOnly]);

  const handleCreateSupplier = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/api/suppliers', formData);
      setShowModal(false);
      fetchData();
    } catch (err) {
      console.error('Error creating supplier:', err);
    }
  };

  const filteredSuppliers = selectedProductId
    ? suppliers.filter((s) => s.product_id === parseInt(selectedProductId))
    : suppliers;

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <div>
          <div className="flex items-center space-x-2 text-emerald-600 font-semibold text-sm mb-1">
            <Truck className="w-4 h-4" />
            <span>Module 2 • Fournisseurs & Sourcing</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-900">Sourcing & Vérification Fournisseurs Fiables</h1>
          <p className="text-sm text-slate-500 mt-1">
            Algorithme de fiabilité automatique : Badge "Fiable" si Ancienneté ≥ 3 ans, Statut Verified Supplier et Taux de réponse &gt; 90%.
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center justify-center space-x-2 px-5 py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded-xl shadow-lg shadow-emerald-900/20 transition"
        >
          <Plus className="w-5 h-5" />
          <span>Nouveau Fournisseur</span>
        </button>
      </div>

      {/* Filter Toolbar */}
      <div className="flex flex-col sm:flex-row justify-between items-center gap-4 bg-white p-4 rounded-xl border border-slate-200">
        <div className="flex items-center space-x-3 w-full sm:w-auto">
          <label className="text-xs font-semibold text-slate-600 whitespace-nowrap">Filtrer par produit :</label>
          <select
            value={selectedProductId}
            onChange={(e) => setSelectedProductId(e.target.value)}
            className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 w-full sm:w-64"
          >
            <option value="">Tous les produits</option>
            {products.map((p) => (
              <option key={p.id} value={p.id}>
                {p.title}
              </option>
            ))}
          </select>
        </div>

        <button
          onClick={() => setReliableOnly(!reliableOnly)}
          className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-bold transition border ${
            reliableOnly
              ? 'bg-emerald-500 text-white border-emerald-600 shadow-sm'
              : 'bg-slate-100 text-slate-700 border-slate-200 hover:bg-slate-200'
          }`}
        >
          <ShieldCheck className="w-4 h-4" />
          <span>Uniquement les Fournisseurs "Fiables"</span>
        </button>
      </div>

      {/* Comparative Table */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <SkeletonCard />
          <SkeletonCard />
        </div>
      ) : filteredSuppliers.length === 0 ? (
        <div className="bg-white rounded-2xl p-12 text-center border border-slate-200">
          <Truck className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <h3 className="text-lg font-bold text-slate-800">Aucun fournisseur répertorié</h3>
          <p className="text-sm text-slate-500 mt-1">Ajoutez un fournisseur pour comparer les prix, MOQ et délais.</p>
        </div>
      ) : (
        <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-600">
              <thead className="bg-slate-50 text-xs uppercase font-bold text-slate-500 border-b border-slate-200">
                <tr>
                  <th className="p-4">Fournisseur & Plateforme</th>
                  <th className="p-4">Statut Fiabilité</th>
                  <th className="p-4">Prix Unitaire</th>
                  <th className="p-4">MOQ (Qté Min)</th>
                  <th className="p-4">Frais Port</th>
                  <th className="p-4">Délais</th>
                  <th className="p-4">Personnalisation</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredSuppliers.map((s) => {
                  const associatedProd = products.find((p) => p.id === s.product_id);
                  return (
                    <tr key={s.id} className="hover:bg-slate-50/80 transition">
                      <td className="p-4">
                        <div className="font-bold text-slate-900">{s.name}</div>
                        <div className="text-xs text-slate-400 flex items-center space-x-2 mt-0.5">
                          <span className="px-2 py-0.5 bg-slate-100 rounded text-slate-600 font-medium">{s.platform}</span>
                          <span>•</span>
                          <span>{s.years_in_business} ans d'ancienneté</span>
                          {associatedProd && (
                            <>
                              <span>•</span>
                              <span className="text-emerald-600 truncate max-w-[150px]">{associatedProd.title}</span>
                            </>
                          )}
                        </div>
                      </td>

                      <td className="p-4">
                        {s.is_reliable ? (
                          <span className="inline-flex items-center space-x-1.5 px-3 py-1 bg-emerald-500/10 text-emerald-600 border border-emerald-500/30 rounded-full text-xs font-bold">
                            <CheckCircle className="w-3.5 h-3.5" />
                            <span>Badge FIABLE</span>
                          </span>
                        ) : (
                          <span className="inline-flex items-center space-x-1.5 px-3 py-1 bg-amber-500/10 text-amber-600 border border-amber-500/30 rounded-full text-xs font-medium">
                            <XCircle className="w-3.5 h-3.5" />
                            <span>Non Vérifié</span>
                          </span>
                        )}
                        <div className="text-[11px] text-slate-400 mt-1">
                          Taux réponse: {s.response_rate}%
                        </div>
                      </td>

                      <td className="p-4 font-bold text-slate-900">{s.unit_price} €</td>
                      <td className="p-4 font-semibold text-slate-700">{s.min_order_quantity} unités</td>
                      <td className="p-4 text-slate-700">{s.shipping_cost} € / unité</td>
                      <td className="p-4 text-slate-700">{s.lead_time_days} jours</td>
                      <td className="p-4 text-slate-700">{s.customization_cost} € / unité</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Creation Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-xl w-full max-h-[90vh] overflow-y-auto p-6 md:p-8 shadow-2xl space-y-6">
            <div className="flex justify-between items-center border-b pb-4">
              <h2 className="text-xl font-bold text-slate-900">Ajouter un Fournisseur</h2>
              <button
                onClick={() => setShowModal(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateSupplier} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Produit Associé</label>
                <select
                  value={formData.product_id}
                  onChange={(e) => setFormData({ ...formData, product_id: parseInt(e.target.value) })}
                  className="w-full px-3 py-2 border rounded-lg text-sm"
                >
                  {products.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.title}
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Nom du Fournisseur</label>
                  <input
                    type="text"
                    required
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Plateforme</label>
                  <select
                    value={formData.platform}
                    onChange={(e) => setFormData({ ...formData, platform: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg text-sm"
                  >
                    <option value="Alibaba">Alibaba</option>
                    <option value="Grossiste">Grossiste Local</option>
                    <option value="Agent">Agent de Sourcing</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4 bg-slate-50 p-4 rounded-xl">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Ancienneté (ans)</label>
                  <input
                    type="number"
                    value={formData.years_in_business}
                    onChange={(e) => setFormData({ ...formData, years_in_business: parseInt(e.target.value) || 0 })}
                    className="w-full px-3 py-2 border rounded-lg text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Taux Réponse (%)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={formData.response_rate}
                    onChange={(e) => setFormData({ ...formData, response_rate: parseFloat(e.target.value) || 0 })}
                    className="w-full px-3 py-2 border rounded-lg text-sm"
                  />
                </div>
                <div className="flex flex-col justify-center">
                  <label className="text-xs font-semibold text-slate-700 mb-1">Statut Verified</label>
                  <label className="inline-flex items-center cursor-pointer space-x-2">
                    <input
                      type="checkbox"
                      checked={formData.is_verified}
                      onChange={(e) => setFormData({ ...formData, is_verified: e.target.checked })}
                      className="rounded text-emerald-600 focus:ring-emerald-500 w-4 h-4"
                    />
                    <span className="text-xs font-medium">Verified Supplier</span>
                  </label>
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Prix Unitaire (€)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.unit_price}
                    onChange={(e) => setFormData({ ...formData, unit_price: parseFloat(e.target.value) || 0 })}
                    className="w-full px-3 py-2 border rounded-lg text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">MOQ (unités)</label>
                  <input
                    type="number"
                    value={formData.min_order_quantity}
                    onChange={(e) => setFormData({ ...formData, min_order_quantity: parseInt(e.target.value) || 1 })}
                    className="w-full px-3 py-2 border rounded-lg text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Frais Port (€)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.shipping_cost}
                    onChange={(e) => setFormData({ ...formData, shipping_cost: parseFloat(e.target.value) || 0 })}
                    className="w-full px-3 py-2 border rounded-lg text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Délai (jours)</label>
                  <input
                    type="number"
                    value={formData.lead_time_days}
                    onChange={(e) => setFormData({ ...formData, lead_time_days: parseInt(e.target.value) || 0 })}
                    className="w-full px-3 py-2 border rounded-lg text-sm"
                  />
                </div>
              </div>

              <div className="flex justify-end space-x-3 pt-4 border-t">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 border rounded-lg text-slate-600 text-sm font-medium"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-sm font-semibold shadow"
                >
                  Enregistrer
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
