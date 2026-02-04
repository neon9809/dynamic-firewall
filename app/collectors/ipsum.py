"""
IPsum collector - fetches IPs from stamparm/ipsum GitHub repository.
"""
import requests
from typing import List, Dict, Any
from datetime import datetime
from .base import BaseCollector


class IpsumCollector(BaseCollector):
    """
    Collector for IPsum threat intelligence feed.
    https://github.com/stamparm/ipsum
    """

    IPSUM_URL = "https://raw.githubusercontent.com/stamparm/ipsum/master/ipsum.txt"

    @property
    def name(self) -> str:
        return "ipsum"

    def fetch(self) -> List[Dict[str, Any]]:
        """
        Fetch IPs from IPsum.
        
        Returns:
            List of IP dictionaries
        """
        self.log_info("Starting to fetch IPs from IPsum...")
        
        min_score = self.config.get('min_score', 3)
        ips = []
        
        try:
            response = requests.get(self.IPSUM_URL, timeout=30)
            response.raise_for_status()
            
            lines = response.text.strip().split('\n')
            
            for line in lines:
                # Skip comments and empty lines
                if line.startswith('#') or not line.strip():
                    continue
                
                # Format: IP\tSCORE
                parts = line.split('\t')
                if len(parts) != 2:
                    continue
                
                ip_address = parts[0].strip()
                try:
                    score = int(parts[1].strip())
                except ValueError:
                    continue
                
                # Filter by minimum score
                if score >= min_score:
                    ips.append({
                        'ip': ip_address,
                        'source': self.name,
                        'score': score,
                        'last_seen': datetime.now()
                    })
            
            self.log_info(f"Successfully fetched {len(ips)} IPs (min_score={min_score})")
            return ips
            
        except requests.RequestException as e:
            self.log_error(f"Failed to fetch IPs: {e}")
            return []
        except Exception as e:
            self.log_error(f"Unexpected error: {e}")
            return []
