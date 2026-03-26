import { useState } from 'react';
import { Toaster, toast } from 'sonner';
import { Shield, Search, AlertTriangle, Phone, User, Hash, Menu, X, Brain } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import SearchForm from '@/components/SearchForm';
import PhoneAnalysisCard from '@/components/PhoneAnalysisCard';
import SocialMediaCard from '@/components/SocialMediaCard';
import WebSearchCard from '@/components/WebSearchCard';
import RiskAnalysisCard from '@/components/RiskAnalysisCard';
import LookupSourcesCard from '@/components/LookupSourcesCard';
import AIAnalysisCard from '@/components/AIAnalysisCard';
import DisclaimerModal from '@/components/DisclaimerModal';
import { apiService } from '@/services/api';
import type { InvestigationResult, SearchType } from '@/types';
import './App.css';

// API Service uses VITE_API_URL from .env.local
const activeApiService = apiService;

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<InvestigationResult | null>(null);
  const [showDisclaimer, setShowDisclaimer] = useState(true);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleSearch = async (query: string, type: SearchType) => {
    setIsLoading(true);
    setResult(null);

    try {
      const response = await activeApiService.investigate(query, type, {
        include_social: true,
        include_web: true,
      });

      if (response.success && response.data) {
        setResult(response.data);
        toast.success('Investigation completed successfully');
      } else {
        toast.error('Investigation failed');
      }
    } catch (error) {
      toast.error('An error occurred during the investigation');
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <Toaster position="top-right" theme="dark" />
      
      {/* Disclaimer Modal */}
      {showDisclaimer && <DisclaimerModal onClose={() => setShowDisclaimer(false)} />}

      {/* Header */}
      <header className="sticky top-0 z-40 w-full border-b border-slate-800 bg-slate-950/80 backdrop-blur-md">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center">
              <Shield className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
                OSINT Phone Intelligence
              </h1>
              <p className="text-xs text-slate-500">Professional Investigation Platform</p>
            </div>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-6">
            <a href="#" className="text-sm text-slate-400 hover:text-slate-200 transition">Dashboard</a>
            <a href="#" className="text-sm text-slate-400 hover:text-slate-200 transition">Documentation</a>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowDisclaimer(true)}
              className="border-slate-700 text-slate-400 hover:text-slate-200"
            >
              <AlertTriangle className="w-4 h-4 mr-2" />
              Disclaimer
            </Button>
          </nav>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden p-2 text-slate-400 hover:text-slate-200"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <nav className="md:hidden border-t border-slate-800 bg-slate-950 px-4 py-4 space-y-3">
            <a href="#" className="block text-sm text-slate-400 hover:text-slate-200">Dashboard</a>
            <a href="#" className="block text-sm text-slate-400 hover:text-slate-200">Documentation</a>
            <button
              onClick={() => {
                setShowDisclaimer(true);
                setMobileMenuOpen(false);
              }}
              className="flex items-center text-sm text-slate-400 hover:text-slate-200"
            >
              <AlertTriangle className="w-4 h-4 mr-2" />
              Disclaimer
            </button>
          </nav>
        )}
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Hero Section */}
        <section className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            <span className="bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400 bg-clip-text text-transparent">
              Phone Number Intelligence
            </span>
          </h2>
          <p className="text-slate-400 max-w-2xl mx-auto mb-8">
            Investigate phone numbers, discover social media profiles, and analyze risk factors 
            with our comprehensive OSINT platform. All searches are conducted ethically and legally.
          </p>

          {/* Search Form */}
          <SearchForm onSearch={handleSearch} isLoading={isLoading} />
        </section>

        {/* Results Section */}
        {result && (
          <section className="space-y-6">
            <div className="flex items-center justify-between">
              <h3 className="text-xl font-semibold text-slate-200">
                Investigation Results
              </h3>
              <div className="text-sm text-slate-500">
                Query: <span className="text-slate-300 font-mono">{result.query}</span>
                <span className="mx-2">|</span>
                Time: <span className="text-slate-300">{result.search_time}s</span>
              </div>
            </div>

            <Tabs defaultValue="overview" className="w-full">
              <TabsList className="grid w-full grid-cols-2 md:grid-cols-6 bg-slate-900">
                <TabsTrigger value="overview" className="data-[state=active]:bg-slate-800">
                  <Phone className="w-4 h-4 mr-2 hidden sm:inline" />
                  Overview
                </TabsTrigger>
                <TabsTrigger value="social" className="data-[state=active]:bg-slate-800">
                  <User className="w-4 h-4 mr-2 hidden sm:inline" />
                  Social
                </TabsTrigger>
                <TabsTrigger value="web" className="data-[state=active]:bg-slate-800">
                  <Search className="w-4 h-4 mr-2 hidden sm:inline" />
                  Web
                </TabsTrigger>
                <TabsTrigger value="risk" className="data-[state=active]:bg-slate-800">
                  <AlertTriangle className="w-4 h-4 mr-2 hidden sm:inline" />
                  Risk
                </TabsTrigger>
                <TabsTrigger value="sources" className="data-[state=active]:bg-slate-800">
                  <Hash className="w-4 h-4 mr-2 hidden sm:inline" />
                  Sources
                </TabsTrigger>
                <TabsTrigger value="ai" className="data-[state=active]:bg-slate-800">
                  <Brain className="w-4 h-4 mr-2 hidden sm:inline" />
                  AI
                </TabsTrigger>
              </TabsList>

              <TabsContent value="overview" className="mt-6">
                {result.phone_analysis && (
                  <PhoneAnalysisCard analysis={result.phone_analysis} />
                )}
              </TabsContent>

              <TabsContent value="social" className="mt-6">
                {result.social_media && (
                  <SocialMediaCard result={result.social_media} />
                )}
              </TabsContent>

              <TabsContent value="web" className="mt-6">
                {result.web_search && (
                  <WebSearchCard results={result.web_search} />
                )}
              </TabsContent>

              <TabsContent value="risk" className="mt-6">
                {result.risk_analysis && (
                  <RiskAnalysisCard analysis={result.risk_analysis} />
                )}
              </TabsContent>

              <TabsContent value="sources" className="mt-6">
                {result.lookup_sources && (
                  <LookupSourcesCard sources={result.lookup_sources} />
                )}
              </TabsContent>

              <TabsContent value="ai" className="mt-6">
                <AIAnalysisCard
                  query={result.query}
                  queryType={result.type}
                  investigationData={result}
                />
              </TabsContent>
            </Tabs>
          </section>
        )}

        {/* Features Grid */}
        {!result && (
          <section className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
            <FeatureCard
              icon={<Phone className="w-6 h-6 text-blue-400" />}
              title="Phone Analysis"
              description="Validate and extract detailed information from any phone number including carrier, location, and type."
            />
            <FeatureCard
              icon={<User className="w-6 h-6 text-indigo-400" />}
              title="Social Media Search"
              description="Discover profiles across Facebook, Instagram, Twitter, LinkedIn, TikTok, Telegram, and more."
            />
            <FeatureCard
              icon={<AlertTriangle className="w-6 h-6 text-amber-400" />}
              title="Risk Assessment"
              description="Comprehensive risk analysis based on multiple factors including spam reports and reputation."
            />
            <FeatureCard
              icon={<Brain className="w-6 h-6 text-purple-400" />}
              title="AI-Powered Insights"
              description="Enhanced analysis using Kimi, Perplexity, and Gemini for deeper investigation insights."
            />
          </section>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 bg-slate-950 mt-16">
        <div className="container mx-auto px-4 py-8">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex items-center gap-3">
              <Shield className="w-5 h-5 text-slate-600" />
              <span className="text-slate-500 text-sm">OSINT Phone Intelligence Platform</span>
            </div>
            <div className="text-slate-600 text-sm text-center md:text-right">
              <p>This tool is for legal OSINT investigations only.</p>
              <p className="mt-1">All searches are logged and monitored.</p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
}

function FeatureCard({ icon, title, description }: FeatureCardProps) {
  return (
    <div className="p-6 rounded-xl bg-slate-900/50 border border-slate-800 hover:border-slate-700 transition">
      <div className="w-12 h-12 rounded-lg bg-slate-800 flex items-center justify-center mb-4">
        {icon}
      </div>
      <h3 className="text-lg font-semibold text-slate-200 mb-2">{title}</h3>
      <p className="text-slate-400 text-sm">{description}</p>
    </div>
  );
}

export default App;
