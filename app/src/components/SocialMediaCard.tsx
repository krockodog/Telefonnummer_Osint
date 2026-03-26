import { User, ExternalLink, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import type { SocialSearchResult, SocialProfile } from '@/types';

interface SocialMediaCardProps {
  result: SocialSearchResult;
}

export default function SocialMediaCard({ result }: SocialMediaCardProps) {
  const platformColors: Record<string, string> = {
    'Facebook': 'bg-blue-600/20 text-blue-400 border-blue-600/30',
    'Instagram': 'bg-pink-600/20 text-pink-400 border-pink-600/30',
    'Twitter/X': 'bg-slate-600/20 text-slate-400 border-slate-600/30',
    'LinkedIn': 'bg-blue-700/20 text-blue-500 border-blue-700/30',
    'TikTok': 'bg-black/40 text-white border-slate-600/30',
    'Telegram': 'bg-sky-600/20 text-sky-400 border-sky-600/30',
    'WhatsApp': 'bg-green-600/20 text-green-400 border-green-600/30',
    'YouTube': 'bg-red-600/20 text-red-400 border-red-600/30',
    'Pinterest': 'bg-red-700/20 text-red-500 border-red-700/30',
    'Snapchat': 'bg-yellow-600/20 text-yellow-400 border-yellow-600/30',
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 70) return 'text-green-400';
    if (confidence >= 40) return 'text-amber-400';
    return 'text-slate-400';
  };

  return (
    <Card className="bg-slate-900 border-slate-800">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-slate-200 flex items-center gap-2">
            <User className="w-5 h-5 text-indigo-400" />
            Social Media Profiles
          </CardTitle>
          <Badge className="bg-indigo-600/20 text-indigo-400 border-indigo-600/30">
            {result.total_found} Found
          </Badge>
        </div>
        <p className="text-sm text-slate-500">
          Query: <span className="font-mono text-slate-400">{result.query}</span>
          <span className="mx-2">|</span>
          Type: <span className="capitalize">{result.query_type}</span>
        </p>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {result.profiles.map((profile, index) => (
            <ProfileItem 
              key={index} 
              profile={profile} 
              platformColor={platformColors[profile.platform] || 'bg-slate-600/20 text-slate-400'}
              confidenceColor={getConfidenceColor(profile.confidence)}
            />
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

interface ProfileItemProps {
  profile: SocialProfile;
  platformColor: string;
  confidenceColor: string;
}

function ProfileItem({ profile, platformColor, confidenceColor }: ProfileItemProps) {
  return (
    <div className={`p-4 rounded-lg border ${profile.found ? 'bg-slate-800/50 border-slate-700' : 'bg-slate-800/20 border-slate-800'} hover:border-slate-600 transition`}>
      <div className="flex items-start justify-between mb-3">
        <Badge className={platformColor}>
          {profile.platform}
        </Badge>
        <div className="flex items-center gap-1">
          {profile.found ? (
            <CheckCircle className="w-4 h-4 text-green-500" />
          ) : (
            <XCircle className="w-4 h-4 text-slate-500" />
          )}
        </div>
      </div>

      <div className="space-y-2">
        {profile.username && (
          <div>
            <p className="text-xs text-slate-500">Username</p>
            <p className="text-sm text-slate-200 font-mono">@{profile.username}</p>
          </div>
        )}

        {profile.display_name && (
          <div>
            <p className="text-xs text-slate-500">Display Name</p>
            <p className="text-sm text-slate-200">{profile.display_name}</p>
          </div>
        )}

        {profile.bio && (
          <div>
            <p className="text-xs text-slate-500">Bio</p>
            <p className="text-sm text-slate-400 line-clamp-2">{profile.bio}</p>
          </div>
        )}

        {profile.followers !== undefined && (
          <div className="flex gap-4">
            <div>
              <p className="text-xs text-slate-500">Followers</p>
              <p className="text-sm text-slate-200">{profile.followers.toLocaleString()}</p>
            </div>
            {profile.following !== undefined && (
              <div>
                <p className="text-xs text-slate-500">Following</p>
                <p className="text-sm text-slate-200">{profile.following.toLocaleString()}</p>
              </div>
            )}
          </div>
        )}

        <div className="flex items-center justify-between pt-2">
          <div className="flex items-center gap-1">
            <span className="text-xs text-slate-500">Confidence:</span>
            <span className={`text-xs font-semibold ${confidenceColor}`}>
              {profile.confidence}%
            </span>
          </div>

          {profile.url && (
            <Button
              variant="outline"
              size="sm"
              className="border-slate-700 text-slate-400 hover:text-slate-200"
              onClick={() => window.open(profile.url, '_blank')}
            >
              <ExternalLink className="w-3 h-3 mr-1" />
              Open
            </Button>
          )}
        </div>

        {profile.error && (
          <div className="flex items-center gap-1 text-xs text-amber-400">
            <AlertCircle className="w-3 h-3" />
            {profile.error}
          </div>
        )}
      </div>
    </div>
  );
}
