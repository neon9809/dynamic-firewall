"""
UniFi syncer - syncs IPs to UniFi Gateway firewall.
"""
import requests
import urllib3
from typing import List, Dict, Any
from .base import BaseSyncer


# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class UniFiSyncer(BaseSyncer):
    """
    Syncer for UniFi Gateway.
    Uses UniFi Network API to manage firewall groups.
    
    API Documentation: https://developer.ui.com/
    """

    @property
    def name(self) -> str:
        return "unifi"

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_url = config.get('api_url', '').rstrip('/')
        self.api_token = config.get('api_token')
        self.site_id = config.get('site_id')
        self.group_name = config.get('group_name', 'd-firewall-blacklist')
        self.verify_ssl = config.get('verify_ssl', False)
        
        self.session = requests.Session()
        self.session.verify = self.verify_ssl
        
        # Set API token in headers
        if self.api_token:
            self.session.headers.update({
                'X-API-KEY': self.api_token,
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            })

    def _get_firewall_group(self) -> Dict[str, Any]:
        """
        Get existing firewall group or create new one.
        
        Returns:
            Firewall group data
        """
        try:
            # List all firewall groups
            list_url = f"{self.api_url}/v1/sites/{self.site_id}/firewall/groups"
            response = self.session.get(list_url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            groups = data.get('data', [])
            
            # Find our group
            for group in groups:
                if group.get('name') == self.group_name:
                    self.log_debug(f"Found existing firewall group: {self.group_name}")
                    return group
            
            # Create new group if not found
            self.log_info(f"Creating new firewall group: {self.group_name}")
            
            create_url = f"{self.api_url}/v1/sites/{self.site_id}/firewall/groups"
            payload = {
                'name': self.group_name,
                'type': 'ipv4-address-group',
                'members': []
            }
            
            response = self.session.post(create_url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result.get('data', {})
            
        except requests.RequestException as e:
            self.log_error(f"Failed to get/create firewall group: {e}")
            if hasattr(e.response, 'text'):
                self.log_debug(f"Response: {e.response.text}")
            return {}

    def _update_firewall_group(self, group_id: str, ips: List[str]) -> bool:
        """
        Update firewall group with new IP list.
        
        Args:
            group_id: Firewall group ID
            ips: List of IP addresses
            
        Returns:
            True if update successful
        """
        try:
            update_url = f"{self.api_url}/v1/sites/{self.site_id}/firewall/groups/{group_id}"
            
            payload = {
                'members': ips,
                'name': self.group_name,
                'type': 'ipv4-address-group'
            }
            
            response = self.session.put(update_url, json=payload, timeout=60)
            response.raise_for_status()
            
            self.log_info(f"Successfully updated firewall group with {len(ips)} IPs")
            return True
            
        except requests.RequestException as e:
            self.log_error(f"Failed to update firewall group: {e}")
            if hasattr(e.response, 'text'):
                self.log_debug(f"Response: {e.response.text}")
            return False

    def sync(self, ips: List[str]) -> bool:
        """
        Sync malicious IPs to UniFi firewall.
        
        Args:
            ips: List of IP addresses to block
            
        Returns:
            True if sync was successful
        """
        self.log_info(f"Starting sync of {len(ips)} IPs to UniFi Gateway...")
        
        # Validate configuration
        if not self.api_token:
            self.log_error("API token not configured")
            return False
        
        if not self.site_id:
            self.log_error("Site ID not configured")
            return False
        
        if not self.api_url:
            self.log_error("API URL not configured")
            return False
        
        # Get or create firewall group
        group = self._get_firewall_group()
        if not group:
            self.log_error("Failed to get firewall group")
            return False
        
        group_id = group.get('id') or group.get('_id')
        if not group_id:
            self.log_error("Invalid firewall group ID")
            return False
        
        # Update the group with new IPs
        return self._update_firewall_group(group_id, ips)
