"""
Phone Number Analyzer Module
Validates and extracts information from phone numbers
"""
import re
import phonenumbers
from phonenumbers import carrier, geocoder, timezone
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class PhoneAnalysisResult:
    """Result of phone number analysis"""
    valid: bool
    e164_format: Optional[str] = None
    international_format: Optional[str] = None
    national_format: Optional[str] = None
    country_code: Optional[str] = None
    country_name: Optional[str] = None
    carrier_name: Optional[str] = None
    location: Optional[str] = None
    timezone: Optional[list] = None
    number_type: Optional[str] = None
    local_number: Optional[str] = None
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'valid': self.valid,
            'e164_format': self.e164_format,
            'international_format': self.international_format,
            'national_format': self.national_format,
            'country_code': self.country_code,
            'country_name': self.country_name,
            'carrier_name': self.carrier_name,
            'location': self.location,
            'timezone': self.timezone,
            'number_type': self.number_type,
            'local_number': self.local_number,
            'error_message': self.error_message
        }


class PhoneAnalyzer:
    """Analyzes phone numbers and extracts metadata"""
    
    # Default region for parsing
    DEFAULT_REGION = 'DE'
    
    # Number type mapping
    NUMBER_TYPES = {
        phonenumbers.PhoneNumberType.MOBILE: 'Mobile',
        phonenumbers.PhoneNumberType.FIXED_LINE: 'Fixed Line',
        phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: 'Fixed or Mobile',
        phonenumbers.PhoneNumberType.TOLL_FREE: 'Toll Free',
        phonenumbers.PhoneNumberType.PREMIUM_RATE: 'Premium Rate',
        phonenumbers.PhoneNumberType.VOIP: 'VoIP',
        phonenumbers.PhoneNumberType.PERSONAL_NUMBER: 'Personal Number',
        phonenumbers.PhoneNumberType.PAGER: 'Pager',
        phonenumbers.PhoneNumberType.UAN: 'UAN',
        phonenumbers.PhoneNumberType.UNKNOWN: 'Unknown',
        phonenumbers.PhoneNumberType.VOICEMAIL: 'Voicemail',
    }
    
    def __init__(self, default_region: str = 'DE'):
        self.default_region = default_region
    
    def clean_number(self, number: str) -> str:
        """Clean phone number by removing non-numeric characters except +"""
        # Keep only digits and +
        cleaned = re.sub(r'[^\d+]', '', number)
        # Remove multiple + signs
        if cleaned.count('+') > 1:
            cleaned = cleaned.replace('+', '', cleaned.count('+') - 1)
        return cleaned
    
    def parse_number(self, number: str, region: Optional[str] = None) -> Optional[phonenumbers.PhoneNumber]:
        """Parse phone number string"""
        try:
            region = region or self.default_region
            cleaned = self.clean_number(number)
            return phonenumbers.parse(cleaned, region)
        except phonenumbers.NumberParseException:
            return None
    
    def analyze(self, number: str, region: Optional[str] = None) -> PhoneAnalysisResult:
        """Analyze a phone number and return detailed information"""
        try:
            parsed = self.parse_number(number, region)
            
            if not parsed:
                return PhoneAnalysisResult(
                    valid=False,
                    error_message="Could not parse phone number"
                )
            
            # Check if valid
            if not phonenumbers.is_valid_number(parsed):
                return PhoneAnalysisResult(
                    valid=False,
                    error_message="Invalid phone number"
                )
            
            # Get number type
            num_type = phonenumbers.number_type(parsed)
            number_type = self.NUMBER_TYPES.get(num_type, 'Unknown')
            
            # Get timezone
            try:
                tz = timezone.time_zones_for_number(parsed)
            except:
                tz = None
            
            # Get location
            try:
                location = geocoder.description_for_number(parsed, 'de')
            except:
                location = None
            
            # Get carrier
            try:
                carrier_name = carrier.name_for_number(parsed, 'de')
            except:
                carrier_name = None
            
            # Get country name
            try:
                country_name = geocoder.country_name_for_number(parsed, 'de')
            except:
                country_name = None
            
            # Get local number (last 10 digits for DE)
            e164 = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
            local_number = e164[-10:] if len(e164) > 10 else e164
            
            return PhoneAnalysisResult(
                valid=True,
                e164_format=e164,
                international_format=phonenumbers.format_number(
                    parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL
                ),
                national_format=phonenumbers.format_number(
                    parsed, phonenumbers.PhoneNumberFormat.NATIONAL
                ),
                country_code=str(parsed.country_code),
                country_name=country_name,
                carrier_name=carrier_name,
                location=location,
                timezone=list(tz) if tz else None,
                number_type=number_type,
                local_number=local_number
            )
            
        except Exception as e:
            return PhoneAnalysisResult(
                valid=False,
                error_message=str(e)
            )
    
    def is_valid(self, number: str, region: Optional[str] = None) -> bool:
        """Quick check if number is valid"""
        parsed = self.parse_number(number, region)
        if not parsed:
            return False
        return phonenumbers.is_valid_number(parsed)
    
    def format_for_search(self, number: str) -> Dict[str, str]:
        """Get various formats for searching"""
        analysis = self.analyze(number)
        if not analysis.valid:
            return {}
        
        return {
            'e164': analysis.e164_format or '',
            'international': analysis.international_format or '',
            'national': analysis.national_format or '',
            'local': analysis.local_number or '',
            'raw': number
        }


# Global analyzer instance
phone_analyzer = PhoneAnalyzer()
