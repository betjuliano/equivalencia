import { use } from 'react';
import AnalysisResultView from '@/components/AnalysisResultView';

export default function AnalysisResult({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  return (
    <div className="container page-content fade-in">
      <AnalysisResultView analysisId={id} />
    </div>
  );
}
