import json
import os
from typing import Optional

import typer

from talos.database.models import ContractDeployment
from talos.database.session import get_session
from talos.tools.contract_deployment import ContractDeploymentTool
from talos.utils.contract_deployment import calculate_contract_signature

contracts_app = typer.Typer()


@contracts_app.command("deploy")
def deploy_contract(
    bytecode_file: str = typer.Argument(..., help="Path to file containing contract bytecode"),
    salt: str = typer.Argument(..., help="Salt for CREATE2 deployment"),
    chain_id: int = typer.Option(42161, "--chain-id", "-c", help="Chain ID to deploy on"),
    constructor_args: Optional[str] = typer.Option(
        None, "--constructor-args", help="JSON array of constructor arguments"
    ),
    check: bool = typer.Option(False, "--check", help="Check for duplicate deployment and prevent if found"),
    gas_limit: Optional[int] = typer.Option(None, "--gas-limit", help="Gas limit for deployment"),
    output_format: str = typer.Option("formatted", "--format", help="Output format: 'formatted' or 'json'"),
):
    """
    Deploy a smart contract with optional duplicate checking.
    """
    try:
        if not os.path.exists(bytecode_file):
            typer.echo(f"Error: Bytecode file not found: {bytecode_file}", err=True)
            raise typer.Exit(1)

        with open(bytecode_file, "r") as f:
            bytecode = f.read().strip()

        parsed_constructor_args = None
        if constructor_args:
            try:
                parsed_constructor_args = json.loads(constructor_args)
            except json.JSONDecodeError:
                typer.echo("Error: Invalid JSON in constructor arguments", err=True)
                raise typer.Exit(1)

        tool = ContractDeploymentTool()
        result = tool._run_unsupervised(
            bytecode=bytecode,
            salt=salt,
            chain_id=chain_id,
            constructor_args=parsed_constructor_args,
            check_duplicates=check,
            gas_limit=gas_limit,
        )

        if output_format == "json":
            print(json.dumps(result.model_dump(), indent=2))
        else:
            print("=== Contract Deployment Result ===")
            print(f"Contract Address: {result.contract_address}")
            print(f"Transaction Hash: {result.transaction_hash}")
            print(f"Chain ID: {result.chain_id}")
            print(f"Contract Signature: {result.contract_signature}")
            if result.gas_used:
                print(f"Gas Used: {result.gas_used}")
            if result.was_duplicate:
                print("⚠️  Duplicate deployment prevented (existing contract returned)")
            else:
                print("✅ New contract deployed successfully")

    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        raise typer.Exit(1)


@contracts_app.command("list")
def list_deployments(
    chain_id: Optional[int] = typer.Option(None, "--chain-id", "-c", help="Filter by chain ID"),
    limit: int = typer.Option(10, "--limit", "-l", help="Maximum number of deployments to show"),
):
    """
    List contract deployments.
    """
    with get_session() as session:
        query = session.query(ContractDeployment)

        if chain_id:
            query = query.filter(ContractDeployment.chain_id == chain_id)

        deployments = query.order_by(ContractDeployment.deployed_at.desc()).limit(limit).all()

        if not deployments:
            print("No deployments found.")
            return

        print("=== Recent Contract Deployments ===")
        for deployment in deployments:
            print(f"Address: {deployment.contract_address}")
            print(f"Chain ID: {deployment.chain_id}")
            print(f"Signature: {deployment.contract_signature}")
            print(f"Deployed: {deployment.deployed_at}")
            print(f"TX Hash: {deployment.transaction_hash}")
            print("-" * 50)


@contracts_app.command("check-duplicate")
def check_duplicate(
    bytecode_file: str = typer.Argument(..., help="Path to file containing contract bytecode"),
    salt: str = typer.Argument(..., help="Salt for CREATE2 deployment"),
    chain_id: int = typer.Option(42161, "--chain-id", "-c", help="Chain ID to check"),
):
    """
    Check if a contract would be a duplicate deployment.
    """
    try:
        if not os.path.exists(bytecode_file):
            typer.echo(f"Error: Bytecode file not found: {bytecode_file}", err=True)
            raise typer.Exit(1)

        with open(bytecode_file, "r") as f:
            bytecode = f.read().strip()

        signature = calculate_contract_signature(bytecode, salt)

        with get_session() as session:
            existing = (
                session.query(ContractDeployment)
                .filter(ContractDeployment.contract_signature == signature, ContractDeployment.chain_id == chain_id)
                .first()
            )

            if existing:
                print("⚠️  Duplicate deployment detected!")
                print(f"Existing contract: {existing.contract_address}")
                print(f"Deployed at: {existing.deployed_at}")
                print(f"Transaction: {existing.transaction_hash}")
            else:
                print("✅ No duplicate found. Safe to deploy.")
                print(f"Contract signature: {signature}")

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
