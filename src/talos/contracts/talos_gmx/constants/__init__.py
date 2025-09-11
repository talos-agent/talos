from eth_typing import HexAddress, HexStr

PRECISION = 30
DATASTORE_ADDRESS = HexAddress(HexStr('0xFD70de6b91282D8017aA4E741e9Ae325CAb992d8'))
SYNTHETICS_ROUTER_CONTRACT_ADDRESS = HexAddress(HexStr('0x7452c558d45f8afC8c83dAe62C3f8A5BE19c71f6'))
EXCHANGE_ROUTER_ADDRESS = HexAddress(HexStr('0x87d66368cD08a7Ca42252f5ab44B2fb6d1Fb8d15'))
ORDER_VAULT_ADDRESS = HexAddress(HexStr('0x31eF83a530Fde1B38EE9A18093A333D8Bbbc40D5'))

USDC_ADDRESS = HexAddress(HexStr('0xaf88d065e77c8cC2239327C5EDb3A432268e5831'))
WETH_ADDRESS = HexAddress(HexStr('0x82aF49447D8a07e3bd95BD0d56f35241523fBab1'))

CONTRACT_MAP = {
    'arbitrum':
    {
        "datastore":
        {
            "contract_address": "0xFD70de6b91282D8017aA4E741e9Ae325CAb992d8",
            "abi_path": "contracts/arbitrum/datastore.json"
        },
        "eventemitter":
        {
            "contract_address": "0xC8ee91A54287DB53897056e12D9819156D3822Fb",
            "abi_path": "contracts/arbitrum/eventemitter.json"
        },
        "exchangerouter":
        {
            "contract_address": "0x900173A66dbD345006C51fA35fA3aB760FcD843b",
            "abi_path": "contracts/arbitrum/exchangerouter.json"
        },
        "depositvault":
        {
            "contract_address": "0xF89e77e8Dc11691C9e8757e84aaFbCD8A67d7A55",
            "abi_path": "contracts/arbitrum/depositvault.json"
        },
        "withdrawalvault":
        {
            "contract_address": "0x0628D46b5D145f183AdB6Ef1f2c97eD1C4701C55",
            "abi_path": "contracts/arbitrum/withdrawalvault.json"
        },
        "ordervault":
        {
            "contract_address": "0x31eF83a530Fde1B38EE9A18093A333D8Bbbc40D5",
            "abi_path": "contracts/arbitrum/ordervault.json"
        },
        "syntheticsreader":
        {
            "contract_address": "0x5Ca84c34a381434786738735265b9f3FD814b824",
            "abi_path": "contracts/arbitrum/syntheticsreader.json"
        },
        "syntheticsrouter":
        {
            "contract_address": "0x7452c558d45f8afC8c83dAe62C3f8A5BE19c71f6",
            "abi_path": "contracts/arbitrum/syntheticsrouter.json"
        },
        "glvreader":
        {
            "contract_address": "0xd4f522c4339Ae0A90a156bd716715547e44Bed65",
            "abi_path": "contracts/arbitrum/glvreader.json"
        }
    },
    'avalanche':
    {
        "datastore":
        {
            "contract_address": "0x2F0b22339414ADeD7D5F06f9D604c7fF5b2fe3f6",
            "abi_path": "contracts/avalanche/datastore.json"
        },
        "eventemitter":
        {
            "contract_address": "0xDb17B211c34240B014ab6d61d4A31FA0C0e20c26",
            "abi_path": "contracts/avalanche/eventemitter.json"
        },
        "exchangerouter":
        {
            "contract_address": "0x2b76df209E1343da5698AF0f8757f6170162e78b",
            "abi_path": "contracts/avalanche/exchangerouter.json"
        },
        "depositvault":
        {
            "contract_address": "0x90c670825d0C62ede1c5ee9571d6d9a17A722DFF",
            "abi_path": "contracts/avalanche/depositvault.json"
        },
        "withdrawalvault":
        {
            "contract_address": "0xf5F30B10141E1F63FC11eD772931A8294a591996",
            "abi_path": "contracts/avalanche/withdrawalvault.json"
        },
        "ordervault":
        {
            "contract_address": "0xD3D60D22d415aD43b7e64b510D86A30f19B1B12C",
            "abi_path": "contracts/avalanche/ordervault.json"
        },
        "syntheticsreader":
        {
            "contract_address": "0xBAD04dDcc5CC284A86493aFA75D2BEb970C72216",
            "abi_path": "contracts/avalanche/syntheticsreader.json"
        },
        "syntheticsrouter":
        {
            "contract_address": "0x820F5FfC5b525cD4d88Cd91aCf2c28F16530Cc68",
            "abi_path": "contracts/avalanche/syntheticsrouter.json"
        }
    }
}
