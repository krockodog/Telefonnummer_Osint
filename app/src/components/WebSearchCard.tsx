import { Search, ExternalLink, Globe } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import type { SearchQueryResult } from '@/types';

interface WebSearchCardProps {
  results: Record<string, SearchQueryResult>;
}

export default function WebSearchCard({ results }: WebSearchCardProps) {
  const resultEntries = Object.entries(results);

  return (
    <Card className="bg-slate-900 border-slate-800">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-slate-200 flex items-center gap-2">
            <Search className="w-5 h-5 text-purple-400" />
            Web Search Results
          </CardTitle>
          <Badge className="bg-purple-600/20 text-purple-400 border-purple-600/30">
            {resultEntries.length} Queries
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <Accordion type="multiple" className="space-y-2">
          {resultEntries.map(([category, data], index) => (
            <AccordionItem 
              key={index} 
              value={`item-${index}`}
              className="border border-slate-800 rounded-lg px-4 data-[state=open]:border-slate-700"
            >
              <AccordionTrigger className="hover:no-underline py-3">
                <div className="flex items-center justify-between w-full pr-4">
                  <div className="flex items-center gap-3">
                    <Globe className="w-4 h-4 text-slate-500" />
                    <span className="text-slate-200 font-medium">{category}</span>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="text-xs text-slate-500">
                      {data.total_results} results
                    </span>
                    <span className="text-xs text-slate-600">
                      {data.search_time.toFixed(2)}s
                    </span>
                  </div>
                </div>
              </AccordionTrigger>
              <AccordionContent>
                <div className="space-y-3 pb-2">
                  {data.error ? (
                    <div className="p-3 rounded bg-red-500/10 border border-red-500/30">
                      <p className="text-sm text-red-400">{data.error}</p>
                    </div>
                  ) : data.results.length === 0 ? (
                    <div className="p-3 rounded bg-slate-800/50">
                      <p className="text-sm text-slate-500">No results found</p>
                    </div>
                  ) : (
                    data.results.map((result, rIndex) => (
                      <SearchResultItem key={rIndex} result={result} />
                    ))
                  )}
                </div>
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </CardContent>
    </Card>
  );
}

interface SearchResultItemProps {
  result: {
    title: string;
    url: string;
    snippet: string;
    source: string;
    position: number;
  };
}

function SearchResultItem({ result }: SearchResultItemProps) {
  return (
    <div className="p-3 rounded-lg bg-slate-800/50 hover:bg-slate-800 transition border border-slate-800 hover:border-slate-700">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <h4 className="text-sm font-medium text-blue-400 hover:text-blue-300 truncate">
            {result.title}
          </h4>
          <p className="text-xs text-slate-500 font-mono truncate mt-1">
            {result.url}
          </p>
          <p className="text-sm text-slate-400 mt-2 line-clamp-2">
            {result.snippet}
          </p>
          <div className="flex items-center gap-3 mt-2">
            <Badge variant="outline" className="text-xs border-slate-700 text-slate-500">
              #{result.position}
            </Badge>
            <span className="text-xs text-slate-600">{result.source}</span>
          </div>
        </div>
        <Button
          variant="ghost"
          size="sm"
          className="shrink-0 text-slate-500 hover:text-slate-300"
          onClick={() => window.open(result.url, '_blank')}
        >
          <ExternalLink className="w-4 h-4" />
        </Button>
      </div>
    </div>
  );
}
