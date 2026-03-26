import { Database, ExternalLink, CheckCircle, XCircle, AlertCircle, Search } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import type { LookupSource } from '@/types';

interface LookupSourcesCardProps {
  sources: LookupSource[];
}

export default function LookupSourcesCard({ sources }: LookupSourcesCardProps) {
  const getStatusIcon = (source: LookupSource) => {
    if (source.reachable === undefined) {
      return <AlertCircle className="w-4 h-4 text-slate-500" />;
    }
    return source.reachable ? (
      <CheckCircle className="w-4 h-4 text-green-500" />
    ) : (
      <XCircle className="w-4 h-4 text-red-500" />
    );
  };

  const getTypeColor = (type: string): string => {
    switch (type) {
      case 'spam_database':
        return 'bg-red-600/20 text-red-400 border-red-600/30';
      case 'reverse_lookup':
        return 'bg-blue-600/20 text-blue-400 border-blue-600/30';
      case 'community_reports':
        return 'bg-amber-600/20 text-amber-400 border-amber-600/30';
      case 'directory':
        return 'bg-green-600/20 text-green-400 border-green-600/30';
      default:
        return 'bg-slate-600/20 text-slate-400 border-slate-600/30';
    }
  };

  const getTypeLabel = (type: string): string => {
    switch (type) {
      case 'spam_database':
        return 'Spam DB';
      case 'reverse_lookup':
        return 'Reverse';
      case 'community_reports':
        return 'Community';
      case 'directory':
        return 'Directory';
      default:
        return type;
    }
  };

  return (
    <Card className="bg-slate-900 border-slate-800">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-slate-200 flex items-center gap-2">
            <Database className="w-5 h-5 text-cyan-400" />
            Lookup Sources
          </CardTitle>
          <Badge className="bg-cyan-600/20 text-cyan-400 border-cyan-600/30">
            {sources.length} Sources
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 gap-3">
          {sources.map((source, index) => (
            <div 
              key={index}
              className="flex items-center justify-between p-4 rounded-lg bg-slate-800/50 border border-slate-800 hover:border-slate-700 transition"
            >
              <div className="flex items-start gap-4">
                <div className="mt-1">
                  {getStatusIcon(source)}
                </div>
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="font-medium text-slate-200">{source.name}</h4>
                    <Badge className={`text-xs ${getTypeColor(source.type)}`}>
                      {getTypeLabel(source.type)}
                    </Badge>
                  </div>
                  <p className="text-sm text-slate-500 mb-1">{source.description}</p>
                  <p className="text-xs text-slate-600 font-mono truncate max-w-md">
                    {source.url}
                  </p>
                  {source.error && (
                    <p className="text-xs text-red-400 mt-1">{source.error}</p>
                  )}
                </div>
              </div>

              <Button
                variant="outline"
                size="sm"
                className="shrink-0 border-slate-700 text-slate-400 hover:text-slate-200"
                onClick={() => window.open(source.url, '_blank')}
              >
                <Search className="w-3 h-3 mr-1" />
                Search
                <ExternalLink className="w-3 h-3 ml-1" />
              </Button>
            </div>
          ))}
        </div>

        <div className="mt-6 p-4 rounded-lg bg-slate-800/30 border border-slate-700">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-amber-400 mt-0.5" />
            <div>
              <h4 className="text-sm font-medium text-slate-200 mb-1">About Lookup Sources</h4>
              <p className="text-sm text-slate-500">
                These external sources can provide additional information about the phone number. 
                Click "Search" to open the source in a new tab. Availability may vary based on 
                the source's current status.
              </p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
