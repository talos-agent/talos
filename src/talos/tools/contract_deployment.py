from __future__ import annotations

import os
from typing import Any, Optional

from pydantic import BaseModel, Field

from talos.database.models import ContractDeployment, User
from talos.database.session import get_session
from talos.models.contract_deployment import ContractDeploymentRequest, ContractDeploymentResult
from talos.utils.contract_deployment import calculate_contract_signature, deploy_contract

from .base import SupervisedTool


class ContractDeploymentArgs(BaseModel):
    bytecode: str = Field(..., description="Contract bytecode to deploy")
    salt: str = Field(..., description="Salt for CREATE2 deployment")
    chain_id: int = Field(42161, description="Chain ID to deploy on")
    constructor_args: Optional[list] = Field(None, description="Constructor arguments")
    check_duplicates: bool = Field(False, description="Check for duplicate deployment and prevent if found")
    gas_limit: Optional[int] = Field(None, description="Gas limit for deployment")


class ContractDeploymentTool(SupervisedTool):
    name: str = "contract_deployment_tool"
    description: str = "Deploy smart contracts with optional duplicate checking"
    args_schema: type[BaseModel] = ContractDeploymentArgs

    def _run_unsupervised(
        self,
        bytecode: str,
        salt: str,
        chain_id: int = 42161,
        constructor_args: Optional[list] = None,
        check_duplicates: bool = False,
        gas_limit: Optional[int] = None,
        **kwargs: Any,
    ) -> ContractDeploymentResult:
        """Deploy a smart contract with optional duplicate checking."""

        signature = calculate_contract_signature(bytecode, salt)

        if check_duplicates:
            with get_session() as session:
                existing = (
                    session.query(ContractDeployment)
                    .filter(ContractDeployment.contract_signature == signature, ContractDeployment.chain_id == chain_id)
                    .first()
                )

                if existing:
                    return ContractDeploymentResult(
                        contract_address=existing.contract_address,
                        transaction_hash=existing.transaction_hash,
                        contract_signature=signature,
                        chain_id=chain_id,
                        gas_used=None,
                        was_duplicate=True,
                    )

        private_key = os.getenv("DEPLOYMENT_PRIVATE_KEY")
        if not private_key:
            raise ValueError("DEPLOYMENT_PRIVATE_KEY environment variable required")

        request = ContractDeploymentRequest(
            bytecode=bytecode,
            salt=salt,
            chain_id=chain_id,
            constructor_args=constructor_args,
            gas_limit=gas_limit,
            gas_price=None,
        )

        result = deploy_contract(request, private_key)

        self._store_deployment(result, signature, salt, bytecode)

        return result

    def _store_deployment(self, result: ContractDeploymentResult, signature: str, salt: str, bytecode: str) -> None:
        """Store deployment record in database."""
        with get_session() as session:
            user = session.query(User).filter(User.user_id == "system").first()
            if not user:
                user = User(user_id="system", is_temporary=False)
                session.add(user)
                session.flush()

            existing_deployment = (
                session.query(ContractDeployment)
                .filter(
                    ContractDeployment.contract_signature == signature, ContractDeployment.chain_id == result.chain_id
                )
                .first()
            )

            if not existing_deployment:
                deployment = ContractDeployment(
                    user_id=user.id,
                    contract_signature=signature,
                    contract_address=result.contract_address,
                    chain_id=result.chain_id,
                    salt=salt,
                    bytecode_hash=signature,
                    transaction_hash=result.transaction_hash,
                    deployment_metadata={"gas_used": result.gas_used, "was_duplicate": result.was_duplicate},
                )
                session.add(deployment)
                session.commit()
