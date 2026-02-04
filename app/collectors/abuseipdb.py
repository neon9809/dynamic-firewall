"""
AbuseIPDB collector - fetches IPs from AbuseIPDB API.
"""
import requests
from typing import List, Dict, Any
from datetime import datetime
from .base import BaseCollector


class AbuseIPDBCollector(BaseCollector):
    """
    Collector for AbuseIPDB threat intelligence feed.
    https://www.abuseipdb.com/
    """

    API_URL = "https://api.abuseipdb.com/api/v2/blacklist"

    @property
    def name(self) -> str:
        return "abuseipdb"

    def fetch(self) -> List[Dict[str, Any]]:
        """
        Fetch IPs from AbuseIPDB blacklist API.
        
        Returns:
            List of IP dictionaries
        """
        self.log_info("Starting to fetch IPs from AbuseIPDB...")
        
        api_key = self.config.get('api_key')
        if not api_key:
            self.log_error("API key not configured")
            return []
        
        confidence_minimum = self.config.get('confidence_minimum', 90)
        limit = self.config.get('limit', 10000)
        
        ips = []
        
        try:
            headers = {
                'Key': api_key,
                'Accept': 'application/json'
            }
            
            params = {
                'confidenceMinimum': confidence_minimum,
                'limit': limit
            }
            
            response = requests.get(
                self.API_URL,
                headers=headers,
                params=params,
                timeout=60
            )
            response.raise_for_status()
            
            data = response.json()
            
            if 'data' in data:
                for entry in data['data']:
                    ip_address = entry.get('ipAddress')
                    score = entry.get('abuseConfidenceScore', 0)
                    
                    if ip_address:
                        ips.append({
                            'ip': ip_address,
                            'source': self.name,
                            'score': score,
                            'last_seen': datetime.now()
                        })
            
            self.log_info(f"Successfully fetched {len(ips)} IPs (confidence>={confidence_minimum})")
            return ips
            
        except requests.RequestException as e:
            self.log_error(f"Failed to fetch IPs: {e}")
            return []
        except Exception as e:
            self.log_error(f"Unexpected error: {e}")
            return []
