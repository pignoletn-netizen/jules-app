import type { Metadata } from 'next';
import '../../public/output.css';
import DashboardLayout from '@/components/DashboardLayout';

export const metadata: Metadata = {
  title: 'MVB Platform - Validation & Automation Business',
  description: 'Plateforme complète de gestion MVB de A à Z',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fr">
      <body>
        <DashboardLayout>{children}</DashboardLayout>
      </body>
    </html>
  );
}
