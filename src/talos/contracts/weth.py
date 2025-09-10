from typing import Annotated

from eth_rpc import ContractFunc, ProtocolBase
from eth_rpc.types import METHOD, Name, NoArgs, primitives


class WETH(ProtocolBase):
    deposit: Annotated[ContractFunc[NoArgs, None], Name("deposit")] = METHOD
    withdraw: Annotated[ContractFunc[primitives.uint256, None], Name("withdraw")] = METHOD
