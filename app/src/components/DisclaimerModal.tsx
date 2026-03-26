import { Shield, AlertTriangle, X, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';

interface DisclaimerModalProps {
  onClose: () => void;
}

export default function DisclaimerModal({ onClose }: DisclaimerModalProps) {
  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl bg-slate-900 border-slate-700 text-slate-100">
        <DialogHeader>
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-full bg-amber-500/20 flex items-center justify-center">
              <AlertTriangle className="w-5 h-5 text-amber-500" />
            </div>
            <DialogTitle className="text-xl text-slate-100">
              Legal Disclaimer & Terms of Use
            </DialogTitle>
          </div>
          <DialogDescription className="text-slate-400">
            Please read and acknowledge the following terms before using this platform.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 mt-4">
          <div className="p-4 rounded-lg bg-slate-800/50 border border-slate-700">
            <h4 className="font-semibold text-slate-200 mb-2 flex items-center gap-2">
              <Shield className="w-4 h-4 text-blue-400" />
              Legal Compliance
            </h4>
            <p className="text-sm text-slate-400">
              This tool is designed for legal OSINT (Open Source Intelligence) investigations only. 
              Users must comply with all applicable laws including GDPR, BDSG, and other data protection 
              regulations. It is prohibited to use this tool for stalking, harassment, or any illegal activities.
            </p>
          </div>

          <div className="p-4 rounded-lg bg-slate-800/50 border border-slate-700">
            <h4 className="font-semibold text-slate-200 mb-2 flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-green-400" />
              Permitted Use Cases
            </h4>
            <ul className="text-sm text-slate-400 space-y-1 list-disc list-inside">
              <li>Verifying unknown callers for personal security</li>
              <li>Investigating potential fraud or scam attempts</li>
              <li>Law enforcement and security research</li>
              <li>Journalistic investigations in the public interest</li>
              <li>Due diligence for business purposes</li>
            </ul>
          </div>

          <div className="p-4 rounded-lg bg-slate-800/50 border border-slate-700">
            <h4 className="font-semibold text-slate-200 mb-2 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-red-400" />
              Data Privacy
            </h4>
            <p className="text-sm text-slate-400">
              This platform does not store search queries or results permanently. All data is processed 
              in memory and automatically deleted after the session. No personal information is collected 
              or shared with third parties.
            </p>
          </div>

          <div className="p-4 rounded-lg bg-amber-500/10 border border-amber-500/30">
            <p className="text-sm text-amber-400">
              <strong>Warning:</strong> Misuse of this tool may result in legal consequences. 
              By clicking "I Understand", you agree to use this platform responsibly and in 
              accordance with all applicable laws.
            </p>
          </div>
        </div>

        <div className="flex justify-end gap-3 mt-6">
          <Button
            variant="outline"
            onClick={onClose}
            className="border-slate-700 text-slate-400 hover:text-slate-200"
          >
            <X className="w-4 h-4 mr-2" />
            Decline
          </Button>
          <Button
            onClick={onClose}
            className="bg-blue-600 hover:bg-blue-700 text-white"
          >
            <CheckCircle className="w-4 h-4 mr-2" />
            I Understand
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
