from eth_rpc import PrivateKeyWallet
from eth_rpc.networks import Arbitrum
from eth_rpc.utils import to_checksum
from eth_typeshed.erc20 import ERC20, ApproveRequest, OwnerSpenderRequest
from eth_typing import HexAddress, HexStr


async def check_if_approved(
    wallet: PrivateKeyWallet,
    spender: HexAddress,
    token_to_approve: HexAddress,
    amount_of_tokens_to_spend: int,
    approve: bool,
):
    if token_to_approve == HexAddress(HexStr("0x47904963fc8b2340414262125aF798B9655E58Cd")):
        token_to_approve = HexAddress(HexStr("0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f"))

    spender_checksum_address = to_checksum(spender)

    # User wallet address will be taken from config file
    user_checksum_address = to_checksum(wallet.address)
    token_checksum_address = to_checksum(token_to_approve)

    token = ERC20[Arbitrum](address=token_to_approve)

    balance_of = await token.balance_of(user_checksum_address).get()

    if balance_of < amount_of_tokens_to_spend:
        raise Exception("Insufficient balance!")

    amount_approved = await token.allowance(
        OwnerSpenderRequest(owner=user_checksum_address, spender=spender_checksum_address)
    ).get()

    print("Checking coins for approval..")
    if amount_approved < amount_of_tokens_to_spend and approve:
        print(
            'Approving contract "{}" to spend {} tokens belonging to token address: {}'.format(
                spender_checksum_address, amount_of_tokens_to_spend, token_checksum_address
            )
        )

        tx_hash = token.approve(
            ApproveRequest(spender=spender_checksum_address, amount=amount_of_tokens_to_spend)
        ).execute(wallet)

        print("Txn submitted!")
        print("Check status: https://arbiscan.io/tx/{}".format(tx_hash.hex()))

    if amount_approved < amount_of_tokens_to_spend and not approve:
        raise Exception("Token not approved for spend, please allow first!")

    print(
        'Contract "{}" approved to spend {} tokens belonging to token address: {}'.format(
            spender_checksum_address, amount_of_tokens_to_spend, token_checksum_address
        )
    )
    print("Coins Approved for spend!")
