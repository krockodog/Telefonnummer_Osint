import { AlertTriangle, Shield, CheckCircle, Info, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import type { RiskAnalysis, RiskLevel } from '@/types';

interface RiskAnalysisCardProps {
  analysis: RiskAnalysis;
}

export default function RiskAnalysisCard({ analysis }: RiskAnalysisCardProps) {
  const getRiskColor = (level: string): string => {
    switch (level as RiskLevel) {
      case 'critical':
        return 'text-red-500 bg-red-500/20 border-red-500/30';
      case 'high':
        return 'text-orange-500 bg-orange-500/20 border-orange-500/30';
      case 'medium':
        return 'text-amber-500 bg-amber-500/20 border-amber-500/30';
      case 'low':
        return 'text-green-500 bg-green-500/20 border-green-500/30';
      default:
        return 'text-slate-500 bg-slate-500/20 border-slate-500/30';
    }
  };

  const getRiskIcon = (level: string) => {
    switch (level as RiskLevel) {
      case 'critical':
      case 'high':
        return <AlertTriangle className="w-5 h-5" />;
      case 'medium':
        return <Info className="w-5 h-5" />;
      case 'low':
        return <CheckCircle className="w-5 h-5" />;
      default:
        return <Minus className="w-5 h-5" />;
    }
  };

  const getProgressColor = (score: number): string => {
    if (score >= 80) return 'bg-red-500';
    if (score >= 60) return 'bg-orange-500';
    if (score >= 40) return 'bg-amber-500';
    if (score >= 20) return 'bg-green-500';
    return 'bg-slate-500';
  };

  const getTrendIcon = (score: number) => {
    if (score >= 60) return <TrendingUp className="w-4 h-4 text-red-400" />;
    if (score <= 20) return <TrendingDown className="w-4 h-4 text-green-400" />;
    return <Minus className="w-4 h-4 text-slate-400" />;
  };

  return (
    <Card className="bg-slate-900 border-slate-800">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-slate-200 flex items-center gap-2">
            <Shield className="w-5 h-5 text-amber-400" />
            Risk Analysis
          </CardTitle>
          <Badge className={getRiskColor(analysis.level)}>
            {getRiskIcon(analysis.level)}
            <span className="ml-1 capitalize">{analysis.level} Risk</span>
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Risk Score */}
        <div className="p-6 rounded-lg bg-slate-800/50 border border-slate-700">
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="text-sm text-slate-500">Overall Risk Score</p>
              <div className="flex items-center gap-2 mt-1">
                <span className={`text-4xl font-bold ${getProgressColor(analysis.score).replace('bg-', 'text-')}`}>
                  {analysis.score}
                </span>
                <span className="text-slate-500">/100</span>
                {getTrendIcon(analysis.score)}
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm text-slate-500">Risk Level</p>
              <p className={`text-lg font-semibold capitalize ${getProgressColor(analysis.score).replace('bg-', 'text-')}`}>
                {analysis.level}
              </p>
            </div>
          </div>
          <div className="relative h-3 bg-slate-700 rounded-full overflow-hidden">
            <div 
              className={`absolute top-0 left-0 h-full transition-all duration-500 ${getProgressColor(analysis.score)}`}
              style={{ width: `${analysis.score}%` }}
            />
          </div>
          <div className="flex justify-between mt-2 text-xs text-slate-500">
            <span>Low Risk</span>
            <span>Medium Risk</span>
            <span>High Risk</span>
          </div>
        </div>

        {/* Risk Factors */}
        <div>
          <h4 className="text-sm font-medium text-slate-300 mb-3">Risk Factors</h4>
          <div className="space-y-2">
            {analysis.factors.map((factor, index) => (
              <div 
                key={index}
                className="flex items-center justify-between p-3 rounded-lg bg-slate-800/30 border border-slate-800 hover:border-slate-700 transition"
              >
                <div className="flex items-center gap-3">
                  <div className={`w-2 h-2 rounded-full ${getProgressColor(factor.score)}`} />
                  <div>
                    <p className="text-sm text-slate-200">{factor.name}</p>
                    <p className="text-xs text-slate-500">{factor.description}</p>
                  </div>
                </div>
                <Badge 
                  variant="outline" 
                  className={`${getProgressColor(factor.score).replace('bg-', 'text-')} border-current`}
                >
                  {factor.score}%
                </Badge>
              </div>
            ))}
          </div>
        </div>

        {/* Recommendations */}
        <div>
          <h4 className="text-sm font-medium text-slate-300 mb-3">Recommendations</h4>
          <div className="space-y-2">
            {analysis.recommendations.map((rec, index) => (
              <div 
                key={index}
                className="flex items-start gap-3 p-3 rounded-lg bg-slate-800/30 border border-slate-800"
              >
                <Info className="w-4 h-4 text-blue-400 mt-0.5 shrink-0" />
                <p className="text-sm text-slate-400">{rec}</p>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
