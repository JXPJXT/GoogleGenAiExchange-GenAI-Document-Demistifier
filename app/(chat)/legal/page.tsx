import { auth } from '@/app/(auth)/auth';
import { LegalAnalysis } from '@/components/legal-analysis';
import { redirect } from 'next/navigation';

export default async function LegalPage() {
  const session = await auth();

  if (!session?.user) {
    redirect('/');
  }

  return (
    <div className="flex flex-1 flex-col">
      <LegalAnalysis />
    </div>
  );
}