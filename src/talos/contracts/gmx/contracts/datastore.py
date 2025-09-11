from typing import Annotated, cast

from eth_rpc import ProtocolBase, ContractFunc
from eth_rpc.networks import Arbitrum
from eth_rpc.types import primitives, Name, NoArgs

from ..constants import DATASTORE_ADDRESS


class Datastore(ProtocolBase):
    add_address: Annotated[
        ContractFunc[
            tuple[primitives.bytes32, primitives.address],
            None
        ],
        Name("addAddress"),
    ]

    add_bytes32: Annotated[
        ContractFunc[
            tuple[primitives.bytes32, primitives.bytes32],
            None
        ],
        Name("addBytes32"),
    ]

    add_uint: Annotated[
        ContractFunc[
            tuple[primitives.bytes32, primitives.uint256],
            None
        ],
        Name("addUint"),
    ]

    address_array_values: Annotated[
        ContractFunc[
            tuple[primitives.bytes32, primitives.uint256],
            primitives.address
        ],
        Name("addressArrayValues"),
    ]

    address_values: Annotated[
        ContractFunc[
            primitives.bytes32,
            primitives.address
        ],
        Name("addressValues"),
    ]

    apply_bounded_delta_to_uint: Annotated[
        ContractFunc[
            tuple[primitives.bytes32, primitives.int256],
            primitives.uint256
        ],
        Name("applyBoundedDeltaToUint"),
    ]

    apply_delta_to_int: Annotated[
        ContractFunc[
            tuple[primitives.bytes32, primitives.int256],
            primitives.int256
        ],
        Name("applyDeltaToInt"),
    ]

    def apply_delta_to_uint(
        self,
        arg1: primitives.bytes32,
        arg2: primitives.int256 | primitives.uint256,
        arg3: primitives.string | None = None,
    ) -> ContractFunc[
        tuple[primitives.bytes32, primitives.int256, primitives.string] | tuple[primitives.bytes32, primitives.uint256],
        primitives.uint256,
    ]:
        if arg3 is None:
            arg2 = cast(primitives.uint256, arg2)
            return self.apply_delta_to_uint_2((arg1, arg2))
        arg2 = cast(primitives.int256, arg2)
        return self.apply_delta_to_uint_1((arg1, arg2, arg3))

    apply_delta_to_uint_1: Annotated[
        ContractFunc[
            tuple[primitives.bytes32, primitives.int256, primitives.string],
            primitives.uint256,
        ],
        Name("applyDeltaToUint"),
    ]

    apply_delta_to_uint_2: Annotated[
        ContractFunc[
            tuple[primitives.bytes32, primitives.uint256],
            primitives.uint256,
        ],
        Name("applyDeltaToUint"),
    ]

    bool_array_values: Annotated[
        ContractFunc[
            tuple[primitives.bytes32, primitives.uint256],
            bool
        ],
        Name("boolArrayValues"),
    ]

    bool_values: Annotated[
        ContractFunc[
            primitives.bytes32,
            bool
        ],
        Name("boolValues"),
    ]

    bytes32_array_values: Annotated[
        ContractFunc[
            tuple[primitives.bytes32, primitives.uint256],
            primitives.bytes32
        ],
        Name("bytes32ArrayValues"),
    ]

    bytes32_values: Annotated[
        ContractFunc[
            primitives.bytes32,
            primitives.bytes32
        ],
        Name("bytes32Values"),
    ]

    contains_address: Annotated[
        ContractFunc[
            tuple[primitives.bytes32, primitives.address],
            bool
        ],
        Name("containsAddress"),
    ]

    contains_bytes32: Annotated[
        ContractFunc[
            tuple[primitives.bytes32, primitives.bytes32],
            bool
        ],
        Name("containsBytes32"),
    ]

    contains_uint: Annotated[
        ContractFunc[
            tuple[primitives.bytes32, primitives.uint256],
            bool
        ],
        Name("containsUint"),
    ]

    decrement_int: Annotated[
        ContractFunc[
            tuple[primitives.bytes32, primitives.int256],
            primitives.int256
        ],
        Name("decrementInt"),
    ]

    decrement_uint: Annotated[
        ContractFunc[
            tuple[primitives.bytes32, primitives.uint256],
            primitives.uint256
        ],
        Name("decrementUint"),
    ]

    get_address: Annotated[
        ContractFunc[
            primitives.bytes32,
            primitives.address
        ],
        Name("getAddress"),
    ]

    get_address_array: Annotated[
        ContractFunc[
            primitives.bytes32,
            list[primitives.address]
        ],
        Name("getAddressArray"),
    ]

    get_address_count: Annotated[
        ContractFunc[
            primitives.bytes32,
            primitives.uint256
        ],
        Name("getAddressCount"),
    ]

    get_address_values_at: Annotated[
        ContractFunc[
            tuple[primitives.bytes32, primitives.uint256, primitives.uint256],
            list[primitives.address]
        ],
        Name("getAddressValuesAt"),
    ]

    get_bool: Annotated[
        ContractFunc[
            primitives.bytes32,
            bool
        ],
        Name("getBool"),
    ]

    get_bool_array: Annotated[
        ContractFunc[
            primitives.bytes32,
            list[bool]
        ],
        Name("getBoolArray"),
    ]

    get_bytes32: Annotated[
        ContractFunc[
            primitives.bytes32,
            primitives.bytes32
        ],
        Name("getBytes32"),
    ]

    get_bytes32_array: Annotated[
        ContractFunc[
            primitives.bytes32,
            list[primitives.bytes32]
        ],
        Name("getBytes32Array"),
    ]

    get_bytes32_count: Annotated[
        ContractFunc[
            primitives.bytes32,
            primitives.uint256
        ],
        Name("getBytes32Count"),
    ]

    get_bytes32_values_at: Annotated[
        ContractFunc[
            tuple[primitives.bytes32, primitives.uint256, primitives.uint256],
            list[primitives.bytes32]
        ],
        Name("getBytes32ValuesAt"),
    ]

    get_int: Annotated[
        ContractFunc[
            primitives.bytes32,
            primitives.int256
        ],
        Name("getInt"),
    ]

    get_int_array: Annotated[
        ContractFunc[
            primitives.bytes32,
            list[primitives.int256]
        ],
        Name("getIntArray"),
    ]

    get_string: Annotated[
        ContractFunc[
            primitives.bytes32,
            primitives.string
        ],
        Name("getString"),
    ]

    get_string_array: Annotated[
        ContractFunc[
            primitives.bytes32,
            list[primitives.string]
        ],
        Name("getStringArray"),
    ]

    get_uint: Annotated[
        ContractFunc[
            primitives.bytes32,
            primitives.uint256
        ],
        Name("getUint"),
    ]

    get_uint_array: Annotated[
        ContractFunc[
            primitives.bytes32,
            list[primitives.uint256]
        ],
        Name("getUintArray"),
    ]

    get_uint_count: Annotated[
        ContractFunc[
            primitives.bytes32,
            primitives.uint256
        ],
        Name("getUintCount"),
    ]

    get_uint_values_at: Annotated[
        ContractFunc[
            tuple[primitives.bytes32, primitives.uint256, primitives.uint256],
            list[primitives.uint256]
        ],
        Name("getUintValuesAt"),
    ]

    increment_int: Annotated[
        ContractFunc[
            tuple[primitives.bytes32, primitives.int256],
            primitives.int256
        ],
        Name("incrementInt"),
    ]

    increment_uint: Annotated[
        ContractFunc[
            tuple[primitives.bytes32, primitives.uint256],
            primitives.uint256
        ],
        Name("incrementUint"),
    ]

    int_array_values: Annotated[
        ContractFunc[
            tuple[primitives.bytes32, primitives.uint256],
            primitives.int256
        ],
        Name("intArrayValues"),
    ]

    int_values: Annotated[
        ContractFunc[
            primitives.bytes32,
            primitives.int256
        ],
        Name("intValues"),
    ]

    remove_address: Annotated[
        ContractFunc[
            tuple[primitives.bytes32, primitives.address],
            None
        ],
        Name("removeAddress"),
    ]

    remove_address_2: Annotated[
        ContractFunc[
            primitives.bytes32,
            None
        ],
        Name("removeAddress"),
    ]

    remove_address_array: Annotated[
        ContractFunc[
            primitives.bytes32,
            None
        ],
        Name("removeAddressArray"),
    ]

    remove_bool: Annotated[
        ContractFunc[
            primitives.bytes32,
            None
        ],
        Name("removeBool"),
    ]

    remove_bool_array: Annotated[
        ContractFunc[
            primitives.bytes32,
            None
        ],
        Name("removeBoolArray"),
    ]

    remove_bytes32: Annotated[
        ContractFunc[
            tuple[primitives.bytes32, primitives.bytes32],
            None
        ],
        Name("removeBytes32"),
    ]

    remove_bytes32_2: Annotated[
        ContractFunc[
            primitives.bytes32,
            None
        ],
        Name("removeBytes32"),
    ]

    remove_bytes32_array: Annotated[
        ContractFunc[
            primitives.bytes32,
            None
        ],
        Name("removeBytes32Array"),
    ]

    remove_int: Annotated[
        ContractFunc[
            primitives.bytes32,
            None
        ],
        Name("removeInt"),
    ]

    remove_int_array: Annotated[
        ContractFunc[
            primitives.bytes32,
            None
        ],
        Name("removeIntArray"),
    ]

    remove_string: Annotated[
        ContractFunc[
            primitives.bytes32,
            None
        ],
        Name("removeString"),
    ]

    remove_string_array: Annotated[
        ContractFunc[
            primitives.bytes32,
            None
        ],
        Name("removeStringArray"),
    ]

    def remove_uint(
        self,
        arg1: primitives.bytes32,
        arg2: primitives.uint256 | None = None,
    ) -> ContractFunc[primitives.bytes32 | tuple[primitives.bytes32, primitives.uint256], None]:
        if arg2 is None:
            return self.remove_uint_1(arg1)
        return self.remove_uint_2((arg1, arg2))

    remove_uint_1: Annotated[
        ContractFunc[
            primitives.bytes32,
            None
        ],
        Name("removeUint"),
    ]

    remove_uint_2: Annotated[
        ContractFunc[
            tuple[primitives.bytes32, primitives.uint256],
            None
        ],
        Name("removeUint"),
    ]

    remove_uint_array: Annotated[
        ContractFunc[
            primitives.bytes32,
            None
        ],
        Name("removeUintArray"),
    ]

    role_store: Annotated[
        ContractFunc[
            NoArgs,
            primitives.address
        ],
        Name("roleStore"),
    ]

    set_address: Annotated[
        ContractFunc[
            tuple[primitives.bytes32, primitives.address],
            primitives.address
        ],
        Name("setAddress"),
    ]

    set_address_array: Annotated[
        ContractFunc[
            tuple[primitives.bytes32, list[primitives.address]],
            None
        ],
        Name("setAddressArray"),
    ]

    set_bool: Annotated[
        ContractFunc[
            tuple[primitives.bytes32, bool],
            bool
        ],
        Name("setBool"),
    ]

    set_bool_array: Annotated[
        ContractFunc[
            tuple[primitives.bytes32, list[bool]],
            None
        ],
        Name("setBoolArray"),
    ]

    set_bytes32: Annotated[
        ContractFunc[
            tuple[primitives.bytes32, primitives.bytes32],
            primitives.bytes32
        ],
        Name("setBytes32"),
    ]

    set_bytes32_array: Annotated[
        ContractFunc[
            tuple[primitives.bytes32, list[primitives.bytes32]],
            None
        ],
        Name("setBytes32Array"),
    ]

    set_int: Annotated[
        ContractFunc[
            tuple[primitives.bytes32, primitives.int256],
            primitives.int256
        ],
        Name("setInt"),
    ]

    set_int_array: Annotated[
        ContractFunc[
            tuple[primitives.bytes32, list[primitives.int256]],
            None
        ],
        Name("setIntArray"),
    ]

    set_string: Annotated[
        ContractFunc[
            tuple[primitives.bytes32, primitives.string],
            primitives.string
        ],
        Name("setString"),
    ]

    set_string_array: Annotated[
        ContractFunc[
            tuple[primitives.bytes32, list[primitives.string]],
            None
        ],
        Name("setStringArray"),
    ]

    set_uint: Annotated[
        ContractFunc[
            tuple[primitives.bytes32, primitives.uint256],
            primitives.uint256
        ],
        Name("setUint"),
    ]

    set_uint_array: Annotated[
        ContractFunc[
            tuple[primitives.bytes32, list[primitives.uint256]],
            None
        ],
        Name("setUintArray"),
    ]

    string_array_values: Annotated[
        ContractFunc[
            tuple[primitives.bytes32, primitives.uint256],
            primitives.string
        ],
        Name("stringArrayValues"),
    ]

    string_values: Annotated[
        ContractFunc[
            primitives.bytes32,
            primitives.string
        ],
        Name("stringValues"),
    ]

    uint_array_values: Annotated[
        ContractFunc[
            tuple[primitives.bytes32, primitives.uint256],
            primitives.uint256
        ],
        Name("uintArrayValues"),
    ]

    uint_values: Annotated[
        ContractFunc[
            primitives.bytes32,
            primitives.uint256
        ],
        Name("uintValues"),
    ]


datastore = Datastore[Arbitrum](address=DATASTORE_ADDRESS)
