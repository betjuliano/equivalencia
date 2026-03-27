'use client';
import AnalysisResultView from '@/components/AnalysisResultView';

export default function AnalysisResult({ params }: { params: { id: string } }) {
  return (
    <div className="container page-content fade-in">
      <AnalysisResultView analysisId={params.id} />
    </div>
  );
}
