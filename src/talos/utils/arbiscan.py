import requests
import json
from typing import Optional, Dict, Any

from talos.models.arbiscan import ContractSourceCode, ContractABI, ArbiScanResponse, ArbiScanABIResponse


class ArbiScanClient:
    """Client for interacting with Arbiscan API to get contract source code and ABI"""
    
    def __init__(self, api_key: Optional[str] = None, chain_id: int = 42161):
        """
        Initialize ArbiScan client
        
        Args:
            api_key: Optional API key for higher rate limits
            chain_id: Chain ID for the network (42161 for Arbitrum One, 42170 for Nova, 421614 for Sepolia)
        """
        self.api_key = api_key
        self.chain_id = chain_id
        self.base_url = "https://api.etherscan.io/v2/api"
    
    def _make_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make a request to the Etherscan API"""
        params["chainid"] = self.chain_id
        if self.api_key:
            params["apikey"] = self.api_key
            
        response = requests.get(self.base_url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_contract_source_code(self, contract_address: str) -> ContractSourceCode:
        """
        Get the source code of a verified contract
        
        Args:
            contract_address: The contract address to get source code for
            
        Returns:
            ContractSourceCode object with the contract details
            
        Raises:
            ValueError: If contract is not verified or not found
            requests.RequestException: If API request fails
        """
        params = {
            "module": "contract",
            "action": "getsourcecode",
            "address": contract_address
        }
        
        data = self._make_request(params)
        response = ArbiScanResponse.model_validate(data)
        
        if response.status != "1":
            raise ValueError(f"Failed to get contract source code: {response.message}")
        
        if isinstance(response.result, str):
            raise ValueError(f"API Error: {response.result}")
        
        if not response.result or not response.result[0].source_code:
            raise ValueError(f"Contract {contract_address} is not verified or does not exist")
        
        return response.result[0]
    
    def get_contract_abi(self, contract_address: str) -> ContractABI:
        """
        Get the ABI of a verified contract
        
        Args:
            contract_address: The contract address to get ABI for
            
        Returns:
            ContractABI object with parsed ABI
            
        Raises:
            ValueError: If contract is not verified or not found
            requests.RequestException: If API request fails
        """
        params = {
            "module": "contract",
            "action": "getabi",
            "address": contract_address
        }
        
        data = self._make_request(params)
        response = ArbiScanABIResponse.model_validate(data)
        
        if response.status != "1":
            raise ValueError(f"Failed to get contract ABI: {response.message}")
        
        if "Missing/Invalid API Key" in response.result or "Invalid API Key" in response.result:
            raise ValueError(f"API Error: {response.result}")
        
        try:
            abi_data = json.loads(response.result)
            return ContractABI(abi=abi_data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid ABI format returned: {e}")


def get_contract_source_code(contract_address: str, api_key: Optional[str] = None, chain_id: int = 42161) -> ContractSourceCode:
    """
    Get the source code of a verified contract
    
    Args:
        contract_address: The contract address to get source code for
        api_key: Optional API key for higher rate limits
        chain_id: Chain ID for the network (default: 42161 for Arbitrum One)
        
    Returns:
        ContractSourceCode object with the contract details
    """
    client = ArbiScanClient(api_key=api_key, chain_id=chain_id)
    return client.get_contract_source_code(contract_address)


def get_contract_abi(contract_address: str, api_key: Optional[str] = None, chain_id: int = 42161) -> ContractABI:
    """
    Get the ABI of a verified contract
    
    Args:
        contract_address: The contract address to get ABI for
        api_key: Optional API key for higher rate limits
        chain_id: Chain ID for the network (default: 42161 for Arbitrum One)
        
    Returns:
        ContractABI object with parsed ABI
    """
    client = ArbiScanClient(api_key=api_key, chain_id=chain_id)
    return client.get_contract_abi(contract_address)
