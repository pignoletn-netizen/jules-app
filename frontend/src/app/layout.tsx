import './globals.css';
import React from 'react';

export const metadata = {
  title: 'Turf Predictor & PMU Bet Advisor',
  description: 'Application de pronostics hippiques et récapitulatif des mises PMU.fr',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fr">
      <body className="bg-slate-900 text-slate-100 antialiased min-h-screen">
        {children}
      </body>
    </html>
  );
}
