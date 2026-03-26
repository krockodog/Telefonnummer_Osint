// OSINT Phone Intelligence Platform - Type Definitions

export interface PhoneAnalysis {
  valid: boolean;
  e164_format?: string;
  international_format?: string;
  national_format?: string;
  country_code?: string;
  country_name?: string;
  carrier_name?: string;
  location?: string;
  timezone?: string[];
  number_type?: string;
  local_number?: string;
  error_message?: string;
}

export interface SocialProfile {
  platform: string;
  username?: string;
  url?: string;
  display_name?: string;
  profile_picture?: string;
  bio?: string;
  followers?: number;
  following?: number;
  posts_count?: number;
  location?: string;
  verified: boolean;
  confidence: number;
  found: boolean;
  error?: string;
}

export interface SocialSearchResult {
  query: string;
  query_type: string;
  profiles: SocialProfile[];
  total_found: number;
  search_time: number;
}

export interface WebSearchResult {
  title: string;
  url: string;
  snippet: string;
  source: string;
  position: number;
}

export interface SearchQueryResult {
  query: string;
  results: WebSearchResult[];
  total_results: number;
  search_time: number;
  error?: string;
}

export interface RiskFactor {
  name: string;
  score: number;
  description: string;
  category: string;
}

export interface RiskAnalysis {
  score: number;
  level: string;
  factors: RiskFactor[];
  recommendations: string[];
}

export interface LookupSource {
  name: string;
  url: string;
  type: string;
  description: string;
  reachable?: boolean;
  status_code?: number;
  error?: string;
}

export interface InvestigationResult {
  query: string;
  type: string;
  timestamp: string;
  search_time: number;
  phone_analysis?: PhoneAnalysis;
  social_media?: SocialSearchResult;
  web_search?: Record<string, SearchQueryResult>;
  lookup_sources?: LookupSource[];
  risk_analysis?: RiskAnalysis;
}

export interface PlatformInfo {
  name: string;
  base_url: string;
  search_url: string;
  profile_url: string;
  icon: string;
  color: string;
}

export type SearchType = 'phone' | 'username' | 'name';
export type RiskLevel = 'unknown' | 'low' | 'medium' | 'high' | 'critical';

// AI Service Types
export interface AIAnalysisResult {
  provider: string;
  query: string;
  response: string;
  sources: Array<{
    title: string;
    url: string;
    snippet?: string;
  }>;
  confidence: number;
  tokens_used?: number;
  processing_time: number;
  error?: string;
  success: boolean;
}

export interface AIStatus {
  available_services: string[];
  kimi: boolean;
  perplexity: boolean;
  gemini: boolean;
}
