from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, List

from talos.core.startup_task import StartupTask

logger = logging.getLogger(__name__)


class InitializeSystemTask(StartupTask):
    """Example one-time startup task for system initialization."""
    
    def __init__(self, **kwargs):
        super().__init__(
            name="initialize_system",
            description="Initialize system components and verify configuration",
            **kwargs
        )
    
    async def run(self, **kwargs: Any) -> str:
        """Initialize system components."""
        logger.info("Running system initialization task")
        
        initialization_steps = [
            "Verify environment variables",
            "Check database connectivity", 
            "Initialize crypto keys",
            "Validate API endpoints"
        ]
        
        for step in initialization_steps:
            logger.info(f"Initialization step: {step}")
        
        completion_time = datetime.now()
        logger.info(f"System initialization completed at {completion_time}")
        return f"System initialization completed at {completion_time}"


class DeployContractTask(StartupTask):
    """Example startup task for contract deployment."""
    
    contract_name: str
    private_key_env: str
    
    def __init__(self, **data):
        super().__init__(**data)
    
    async def run(self, **kwargs: Any) -> str:
        """Deploy a smart contract."""
        logger.info(f"Deploying contract: {self.contract_name}")
        
        deployment_steps = [
            f"Load private key from {self.private_key_env}",
            f"Compile {self.contract_name} contract",
            "Deploy to network",
            "Verify deployment"
        ]
        
        for step in deployment_steps:
            logger.info(f"Contract deployment step: {step}")
        
        completion_time = datetime.now()
        logger.info(f"Contract {self.contract_name} deployed at {completion_time}")
        return f"Contract {self.contract_name} deployed successfully at {completion_time}"


class HealthCheckTask(StartupTask):
    """Example recurring startup task for health monitoring."""
    
    def __init__(self, **kwargs):
        super().__init__(
            name="startup_health_check",
            description="Recurring health check for daemon startup components",
            cron_expression="*/5 * * * *",
            **kwargs
        )
    
    async def run(self, **kwargs: Any) -> str:
        """Perform health check."""
        logger.info("Running startup health check")
        
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "startup_system": "healthy",
            "task_manager": "operational"
        }
        
        logger.info(f"Startup health check completed: {health_status}")
        return f"Startup health check completed: {health_status['startup_system']}"


def create_example_startup_tasks() -> List[StartupTask]:
    """
    Create example startup tasks for demonstration.
    
    Returns:
        List of example StartupTask instances
    """
    tasks = [
        InitializeSystemTask(),
        DeployContractTask(
            name="deploy_contract_TalosGovernance",
            description="Deploy TalosGovernance contract using private key from TALOS_DEPLOY_KEY",
            contract_name="TalosGovernance",
            private_key_env="TALOS_DEPLOY_KEY"
        ),
        HealthCheckTask()
    ]
    
    return tasks
