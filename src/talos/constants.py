from eth_typing import HexAddress, HexStr


class WETH:
    ARBITRUM = HexAddress(HexStr("0x82aF49447D8a07e3bd95BD0d56f35241523fBab1"))


class OHM:
    ARBITRUM = HexAddress(HexStr("0xf0cb2dc0db5e6c66B9a70Ac27B06b878da017028"))


class CamelotYakSwapConstants:
    ADAPTER = HexAddress(HexStr("0x610934FEBC44BE225ADEcD888eAF7DFf3B0bc050"))
    ROUTER = HexAddress(HexStr("0x99D4e80DB0C023EFF8D25d8155E0dCFb5aDDeC5E"))


class CamelotPoolAddresses:
    OHM_ETH = HexAddress(HexStr("0x8aCd42e4B5A5750B44A28C5fb50906eBfF145359"))
