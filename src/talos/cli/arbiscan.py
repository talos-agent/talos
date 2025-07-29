from typing import Optional
import os
import typer
import json

from talos.utils.arbiscan import get_contract_source_code

arbiscan_app = typer.Typer()


@arbiscan_app.command("get-source-code")
def get_source_code(
    contract_address: str = typer.Argument(..., help="The contract address to get source code for"),
    api_key: Optional[str] = typer.Option(None, "--api-key", "-k", help="Optional API key for higher rate limits"),
    chain_id: int = typer.Option(42161, "--chain-id", "-c", help="Chain ID (42161 for Arbitrum One, 42170 for Nova, 421614 for Sepolia)"),
    output_format: str = typer.Option("formatted", "--format", "-f", help="Output format: 'formatted', 'json', or 'source-only'"),
):
    """
    Gets the source code of a verified smart contract from Arbiscan.
    """
    try:
        api_key = api_key or os.getenv("ARBISCAN_API_KEY")
        contract_data = get_contract_source_code(
            contract_address=contract_address,
            api_key=api_key,
            chain_id=chain_id
        )
        
        if output_format == "json":
            print(json.dumps(contract_data.model_dump(), indent=2))
        elif output_format == "source-only":
            print(contract_data.source_code)
        else:
            print(f"=== Contract Source Code for {contract_address} ===\n")
            print(f"Contract Name: {contract_data.contract_name}")
            print(f"Compiler Version: {contract_data.compiler_version}")
            print(f"Optimization Used: {contract_data.optimization_used}")
            if contract_data.optimization_used == "1":
                print(f"Optimization Runs: {contract_data.runs}")
            print(f"License Type: {contract_data.license_type}")
            if contract_data.proxy == "1":
                print(f"Proxy Implementation: {contract_data.implementation}")
            print("\n" + "="*50 + " SOURCE CODE " + "="*50)
            print(contract_data.source_code)
            
    except ValueError as e:
        error_msg = str(e)
        if "NOTOK" in error_msg or "Missing/Invalid API Key" in error_msg:
            typer.echo("Error: Arbiscan API key is required to get contract source code.", err=True)
            typer.echo("Please provide an API key using the --api-key option.", err=True)
            typer.echo("You can get a free API key from https://arbiscan.io/apis", err=True)
        else:
            typer.echo(f"Error: {error_msg}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        raise typer.Exit(1)
