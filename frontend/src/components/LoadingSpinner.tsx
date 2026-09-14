import React from 'react';

export default function LoadingSpinner({ size = 'medium', text = 'Chargement en cours...' }: { size?: 'small' | 'medium' | 'large', text?: string }) {
  const sizeClasses = {
    small: 'w-4 h-4 border-2',
    medium: 'w-8 h-8 border-3',
    large: 'w-12 h-12 border-4',
  };

  return (
    <div className="flex flex-col items-center justify-center p-6 space-y-3">
      <div
        className={`${sizeClasses[size]} border-emerald-600 border-t-transparent rounded-full animate-spin`}
      />
      {text && <p className="text-sm font-medium text-slate-600 animate-pulse">{text}</p>}
    </div>
  );
}

export function SkeletonCard() {
  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200 animate-pulse space-y-4">
      <div className="h-6 bg-slate-200 rounded w-1/3"></div>
      <div className="h-4 bg-slate-100 rounded w-full"></div>
      <div className="h-4 bg-slate-100 rounded w-2/3"></div>
      <div className="flex justify-between pt-4">
        <div className="h-8 bg-slate-200 rounded w-24"></div>
        <div className="h-8 bg-emerald-100 rounded w-28"></div>
      </div>
    </div>
  );
}
