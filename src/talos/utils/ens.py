import os
from typing import Optional
from web3 import Web3
from web3.providers import HTTPProvider

from talos.models.ens import ENSResolution, ReverseENSResolution


class ENSClient:
    """Client for interacting with ENS (Ethereum Name Service) on mainnet"""
    
    def __init__(self, provider_url: Optional[str] = None):
        """
        Initialize ENS client
        
        Args:
            provider_url: Optional custom RPC provider URL. Defaults to Infura mainnet.
        """
        if provider_url is None:
            infura_project_id = os.getenv("INFURA_PROJECT_ID", "")
            if infura_project_id:
                provider_url = f"https://mainnet.infura.io/v3/{infura_project_id}"
            else:
                provider_url = "https://eth.llamarpc.com"
        
        self.w3 = Web3(HTTPProvider(provider_url))
        
        if not self.w3.is_connected():
            raise ConnectionError(f"Failed to connect to Ethereum provider: {provider_url}")
    
    def resolve_name(self, ens_name: str) -> ENSResolution:
        """
        Resolve an ENS name to an Ethereum address
        
        Args:
            ens_name: The ENS name to resolve (e.g., "vitalik.eth")
            
        Returns:
            ENSResolution object with the resolved address
            
        Raises:
            ValueError: If the ENS name format is invalid
            ConnectionError: If unable to connect to Ethereum network
        """
        from talos.utils.validation import sanitize_user_input
        ens_name = sanitize_user_input(ens_name, max_length=100).lower().strip()
        
        if not ens_name.endswith('.eth'):
            raise ValueError(f"Invalid ENS name format: {ens_name}. ENS names must end with .eth")
        
        try:
            address = self.w3.ens.address(ens_name)  # type: ignore[union-attr]
            
            if address is None:
                return ENSResolution(
                    ens_name=ens_name,
                    address="",
                    is_valid=False
                )
            
            return ENSResolution(
                ens_name=ens_name,
                address=str(address),
                is_valid=True
            )
            
        except Exception as e:
            raise ValueError(f"Failed to resolve ENS name {ens_name}: {str(e)}")
    
    def reverse_resolve(self, address: str) -> ReverseENSResolution:
        """
        Perform reverse ENS resolution to get the ENS name for an address
        
        Args:
            address: The Ethereum address to reverse resolve
            
        Returns:
            ReverseENSResolution object with the ENS name if found
            
        Raises:
            ValueError: If the address format is invalid
            ConnectionError: If unable to connect to Ethereum network
        """
        from talos.utils.validation import sanitize_user_input
        address = sanitize_user_input(address, max_length=100).strip()
        
        if not self.w3.is_address(address):
            raise ValueError(f"Invalid Ethereum address format: {address}")
        
        address = self.w3.to_checksum_address(address)
        
        try:
            resolved_name = self.w3.ens.name(address)  # type: ignore[union-attr]
            
            return ReverseENSResolution(
                address=address,
                ens_name=resolved_name,
                is_valid=resolved_name is not None
            )
            
        except Exception as e:
            raise ValueError(f"Failed to reverse resolve address {address}: {str(e)}")


def resolve_ens_name(ens_name: str, provider_url: Optional[str] = None) -> ENSResolution:
    """
    Resolve an ENS name to an Ethereum address
    
    Args:
        ens_name: The ENS name to resolve (e.g., "vitalik.eth")
        provider_url: Optional custom RPC provider URL
        
    Returns:
        ENSResolution object with the resolved address
    """
    client = ENSClient(provider_url=provider_url)
    return client.resolve_name(ens_name)


def reverse_resolve_address(address: str, provider_url: Optional[str] = None) -> ReverseENSResolution:
    """
    Perform reverse ENS resolution to get the ENS name for an address
    
    Args:
        address: The Ethereum address to reverse resolve
        provider_url: Optional custom RPC provider URL
        
    Returns:
        ReverseENSResolution object with the ENS name if found
    """
    client = ENSClient(provider_url=provider_url)
    return client.reverse_resolve(address)
