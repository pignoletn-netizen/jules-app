'use client';

import React, { useState, useEffect } from 'react';
import {
  ShieldCheck,
  FileCheck,
  Plus,
  CheckCircle2,
  AlertCircle,
  FileText,
  Clock,
  Check,
  X
} from 'lucide-react';
import api from '@/lib/api';
import LoadingSpinner, { SkeletonCard } from '@/components/LoadingSpinner';

export default function CompliancePage() {
  const [products, setProducts] = useState<any[]>([]);
  const [selectedProductId, setSelectedProductId] = useState<number>(0);
  const [compliance, setCompliance] = useState<any>(null);
  const [documents, setDocuments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showDocModal, setShowDocModal] = useState(false);

  const [docType, setDocType] = useState('Certificat CE');
  const [docName, setDocName] = useState('');
  const [docStatus, setDocStatus] = useState('Validated');

  const fetchProducts = async () => {
    try {
      const res = await api.get('/api/products');
      setProducts(res.data);
      if (res.data.length > 0 && selectedProductId === 0) {
        setSelectedProductId(res.data[0].id);
      }
    } catch (err) {
      console.error('Error fetching products:', err);
    }
  };

  const fetchComplianceData = async (pId: number) => {
    if (!pId) return;
    setLoading(true);
    try {
      const [compRes, docRes] = await Promise.all([
        api.get(`/api/compliance/${pId}`),
        api.get(`/api/compliance/documents/${pId}`),
      ]);
      setCompliance(compRes.data);
      setDocuments(docRes.data);
    } catch (err) {
      console.error('Error fetching compliance data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  useEffect(() => {
    if (selectedProductId) {
      fetchComplianceData(selectedProductId);
    }
  }, [selectedProductId]);

  const toggleChecklistField = async (field: string, currentVal: boolean) => {
    try {
      const updated = await api.put(`/api/compliance/${selectedProductId}`, {
        [field]: !currentVal,
      });
      setCompliance(updated.data);
    } catch (err) {
      console.error('Error updating checklist:', err);
    }
  };

  const handleAddDocument = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/api/compliance/documents', {
        product_id: selectedProductId,
        doc_type: docType,
        doc_name: docName,
        status: docStatus,
      });
      setShowDocModal(false);
      setDocName('');
      fetchComplianceData(selectedProductId);
    } catch (err) {
      console.error('Error adding document:', err);
    }
  };

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <div>
          <div className="flex items-center space-x-2 text-emerald-600 font-semibold text-sm mb-1">
            <ShieldCheck className="w-4 h-4" />
            <span>Module 4 • Conformité & Normes UE</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-900">Checklist Réglementaire & Documents d'Importation</h1>
          <p className="text-sm text-slate-500 mt-1">
            Suivi automatique du Marquage CE, RoHS, étiquetage obligatoire en français et numéro EORI.
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
                {p.title} ({p.category})
              </option>
            ))}
          </select>
        </div>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <SkeletonCard />
          <SkeletonCard />
        </div>
      ) : compliance ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Regulatory Checklist Card */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-6">
            <div className="flex justify-between items-center border-b pb-4">
              <h2 className="text-lg font-bold text-slate-900 flex items-center space-x-2">
                <ShieldCheck className="w-5 h-5 text-emerald-600" />
                <span>Normes Européennes ({compliance.category})</span>
              </h2>
            </div>

            <div className="space-y-4">
              {/* CE Marking */}
              <div
                onClick={() => toggleChecklistField('ce_marking', compliance.ce_marking)}
                className="flex items-center justify-between p-4 rounded-xl border border-slate-200 hover:border-emerald-500/50 cursor-pointer transition bg-slate-50/50"
              >
                <div>
                  <h4 className="text-sm font-bold text-slate-900">Marquage CE Obligatoire</h4>
                  <p className="text-xs text-slate-500">
                    Déclaration UE de conformité du fabricant ou mandataire européen.
                  </p>
                </div>
                <div
                  className={`w-6 h-6 rounded-lg flex items-center justify-center font-bold text-white transition ${
                    compliance.ce_marking ? 'bg-emerald-500' : 'bg-slate-200'
                  }`}
                >
                  {compliance.ce_marking && <Check className="w-4 h-4" />}
                </div>
              </div>

              {/* RoHS */}
              <div
                onClick={() => toggleChecklistField('rohs_compliant', compliance.rohs_compliant)}
                className="flex items-center justify-between p-4 rounded-xl border border-slate-200 hover:border-emerald-500/50 cursor-pointer transition bg-slate-50/50"
              >
                <div>
                  <h4 className="text-sm font-bold text-slate-900">Conformité RoHS</h4>
                  <p className="text-xs text-slate-500">
                    Restriction des substances dangereuses dans les équipements électroniques.
                  </p>
                </div>
                <div
                  className={`w-6 h-6 rounded-lg flex items-center justify-center font-bold text-white transition ${
                    compliance.rohs_compliant ? 'bg-emerald-500' : 'bg-slate-200'
                  }`}
                >
                  {compliance.rohs_compliant && <Check className="w-4 h-4" />}
                </div>
              </div>

              {/* Mandatory Labeling */}
              <div
                onClick={() => toggleChecklistField('mandatory_labeling', compliance.mandatory_labeling)}
                className="flex items-center justify-between p-4 rounded-xl border border-slate-200 hover:border-emerald-500/50 cursor-pointer transition bg-slate-50/50"
              >
                <div>
                  <h4 className="text-sm font-bold text-slate-900">Étiquetage Obligatoire en Français</h4>
                  <p className="text-xs text-slate-500">
                    Règles d'emballage, nom/adresse de l'importateur EU et consignes de sécurité.
                  </p>
                </div>
                <div
                  className={`w-6 h-6 rounded-lg flex items-center justify-center font-bold text-white transition ${
                    compliance.mandatory_labeling ? 'bg-emerald-500' : 'bg-slate-200'
                  }`}
                >
                  {compliance.mandatory_labeling && <Check className="w-4 h-4" />}
                </div>
              </div>
            </div>

            {/* Custom Rules List */}
            {compliance.custom_rules && compliance.custom_rules.length > 0 && (
              <div className="pt-4 border-t border-slate-100">
                <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                  Directives Spécifiques à la Catégorie
                </h4>
                <ul className="space-y-1.5 text-xs text-slate-600">
                  {compliance.custom_rules.map((rule: string, idx: number) => (
                    <li key={idx} className="flex items-start space-x-2">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 flex-shrink-0 mt-0.5" />
                      <span>{rule}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Import Documents Tracker */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-6">
            <div className="flex justify-between items-center border-b pb-4">
              <h2 className="text-lg font-bold text-slate-900 flex items-center space-x-2">
                <FileCheck className="w-5 h-5 text-emerald-600" />
                <span>Documents d'Importation & Douanes</span>
              </h2>
              <button
                onClick={() => setShowDocModal(true)}
                className="flex items-center space-x-1 px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold"
              >
                <Plus className="w-4 h-4" />
                <span>Ajouter Doc</span>
              </button>
            </div>

            {documents.length === 0 ? (
              <div className="text-center py-8 text-slate-400 text-sm">
                <FileText className="w-10 h-10 mx-auto mb-2 text-slate-300" />
                <span>Aucun document joint pour le moment.</span>
              </div>
            ) : (
              <div className="space-y-3">
                {documents.map((doc) => (
                  <div
                    key={doc.id}
                    className="flex items-center justify-between p-4 bg-slate-50 rounded-xl border border-slate-200 text-sm"
                  >
                    <div>
                      <p className="font-bold text-slate-900">{doc.doc_name}</p>
                      <p className="text-xs text-slate-500">{doc.doc_type}</p>
                    </div>

                    <span
                      className={`px-3 py-1 rounded-full text-xs font-bold border ${
                        doc.status === 'Validated'
                          ? 'bg-emerald-500/10 text-emerald-600 border-emerald-500/30'
                          : doc.status === 'Pending'
                          ? 'bg-amber-500/10 text-amber-600 border-amber-500/30'
                          : 'bg-rose-500/10 text-rose-600 border-rose-500/30'
                      }`}
                    >
                      {doc.status === 'Validated' ? 'Validé' : doc.status === 'Pending' ? 'En Attente' : 'Manquant'}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      ) : null}

      {/* Doc Modal */}
      {showDocModal && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-6">
            <div className="flex justify-between items-center border-b pb-4">
              <h2 className="text-lg font-bold text-slate-900">Ajouter un Document Douanier</h2>
              <button onClick={() => setShowDocModal(false)} className="p-1 rounded-lg text-slate-400">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleAddDocument} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Type de Document</label>
                <select
                  value={docType}
                  onChange={(e) => setDocType(e.target.value)}
                  className="w-full px-3 py-2 border rounded-lg text-sm"
                >
                  <option value="Certificat CE">Certificat CE / Conformité</option>
                  <option value="Numéro EORI">Numéro EORI Importateur</option>
                  <option value="Facture Douanière">Facture Douanière & COGS</option>
                  <option value="Rapport de Test Labo">Rapport de Test Laboratoire</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Nom / Référence du Fichier</label>
                <input
                  type="text"
                  required
                  value={docName}
                  onChange={(e) => setDocName(e.target.value)}
                  placeholder="Certificat_Conformite_2026.pdf"
                  className="w-full px-3 py-2 border rounded-lg text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Statut</label>
                <select
                  value={docStatus}
                  onChange={(e) => setDocStatus(e.target.value)}
                  className="w-full px-3 py-2 border rounded-lg text-sm"
                >
                  <option value="Validated">Validé (Conforme)</option>
                  <option value="Pending">En Attente de Vérification</option>
                  <option value="Missing">Manquant</option>
                </select>
              </div>

              <div className="flex justify-end space-x-3 pt-4 border-t">
                <button
                  type="button"
                  onClick={() => setShowDocModal(false)}
                  className="px-4 py-2 border rounded-lg text-slate-600 text-sm font-medium"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-sm font-semibold shadow"
                >
                  Ajouter
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
