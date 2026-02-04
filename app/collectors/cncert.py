"""
CNCERT collector - fetches IPs from China National Computer Network Emergency Response Team.
"""
import re
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from datetime import datetime
from .base import BaseCollector


class CNCERTCollector(BaseCollector):
    """
    Collector for CNCERT threat intelligence.
    https://www.cert.org.cn/
    """

    # CNCERT publishes IPs in news articles and reports
    BASE_URL = "https://www.cert.org.cn"
    THREAT_URL = f"{BASE_URL}/publish/main/9/index.html"

    @property
    def name(self) -> str:
        return "cncert"

    def fetch(self) -> List[Dict[str, Any]]:
        """
        Fetch IPs from CNCERT announcements.
        
        Returns:
            List of IP dictionaries
        """
        self.log_info("Starting to fetch IPs from CNCERT...")
        
        ips = []
        ip_pattern = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')
        
        try:
            # Fetch the threat announcement page
            response = requests.get(self.THREAT_URL, timeout=30)
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all links to threat announcements
            links = soup.find_all('a', href=True)
            
            # Limit to recent announcements
            max_articles = self.config.get('max_articles', 5)
            article_count = 0
            
            for link in links:
                if article_count >= max_articles:
                    break
                
                href = link.get('href', '')
                
                # Look for announcement articles
                if 'ARTI' in href or 'article' in href.lower():
                    article_url = href if href.startswith('http') else f"{self.BASE_URL}{href}"
                    
                    try:
                        article_response = requests.get(article_url, timeout=20)
                        article_response.encoding = 'utf-8'
                        
                        # Extract IPs from article text
                        found_ips = ip_pattern.findall(article_response.text)
                        
                        for ip in found_ips:
                            # Basic validation
                            if self._is_valid_ip(ip):
                                ips.append({
                                    'ip': ip,
                                    'source': self.name,
                                    'score': 5,  # Default score for CNCERT
                                    'last_seen': datetime.now()
                                })
                        
                        article_count += 1
                        
                    except Exception as e:
                        self.log_debug(f"Failed to fetch article {article_url}: {e}")
                        continue
            
            # Remove duplicates
            unique_ips = {}
            for ip_data in ips:
                ip = ip_data['ip']
                if ip not in unique_ips:
                    unique_ips[ip] = ip_data
            
            result = list(unique_ips.values())
            self.log_info(f"Successfully fetched {len(result)} unique IPs from CNCERT")
            return result
            
        except requests.RequestException as e:
            self.log_error(f"Failed to fetch IPs: {e}")
            return []
        except Exception as e:
            self.log_error(f"Unexpected error: {e}")
            return []

    def _is_valid_ip(self, ip: str) -> bool:
        """
        Validate if the IP address is valid and not private.
        
        Args:
            ip: IP address string
            
        Returns:
            True if valid public IP
        """
        try:
            parts = ip.split('.')
            if len(parts) != 4:
                return False
            
            # Check each octet
            for part in parts:
                num = int(part)
                if num < 0 or num > 255:
                    return False
            
            # Exclude private and reserved IPs
            first_octet = int(parts[0])
            
            # Private ranges: 10.x.x.x, 172.16-31.x.x, 192.168.x.x
            if first_octet == 10:
                return False
            if first_octet == 172 and 16 <= int(parts[1]) <= 31:
                return False
            if first_octet == 192 and int(parts[1]) == 168:
                return False
            
            # Loopback: 127.x.x.x
            if first_octet == 127:
                return False
            
            # Reserved: 0.x.x.x, 255.x.x.x
            if first_octet == 0 or first_octet == 255:
                return False
            
            return True
            
        except (ValueError, IndexError):
            return False
