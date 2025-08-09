from __future__ import annotations

import asyncio
import logging
import os
import signal
import sys
from typing import Optional

from langchain_openai import ChatOpenAI

from talos.core.main_agent import MainAgent
from talos.settings import OpenAISettings

logger = logging.getLogger(__name__)


class TalosDaemon:
    def __init__(self, prompts_dir: str = "src/talos/prompts", model_name: str = "gpt-5", temperature: float = 0.0):
        self.prompts_dir = prompts_dir
        self.model_name = model_name
        self.temperature = temperature
        self.main_agent: Optional[MainAgent] = None
        self.shutdown_event = asyncio.Event()
        
    def _validate_environment(self) -> None:
        OpenAISettings()
        
        if not os.path.exists(self.prompts_dir):
            raise FileNotFoundError(f"Prompts directory not found at {self.prompts_dir}")
    
    def _setup_signal_handlers(self) -> None:
        def signal_handler(signum: int, frame) -> None:
            logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            asyncio.create_task(self._shutdown())
        
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
    
    async def _shutdown(self) -> None:
        logger.info("Starting graceful shutdown...")
        
        if self.main_agent and self.main_agent.job_scheduler:
            logger.info("Stopping job scheduler...")
            self.main_agent.job_scheduler.stop()
            logger.info("Job scheduler stopped")
        
        self.shutdown_event.set()
        logger.info("Shutdown complete")
    
    def _initialize_agent(self) -> None:
        logger.info("Initializing MainAgent...")
        
        model = ChatOpenAI(model=self.model_name, temperature=self.temperature)
        
        self.main_agent = MainAgent(
            prompts_dir=self.prompts_dir,
            model=model,
            schema=None,
        )
        
        logger.info("MainAgent initialized successfully")
        
        if self.main_agent.startup_task_manager:
            logger.info("Executing startup tasks...")
            import asyncio
            asyncio.create_task(self.main_agent.startup_task_manager.execute_pending_tasks())
            logger.info("Startup tasks execution initiated")
        
        if self.main_agent.job_scheduler:
            logger.info(f"Job scheduler is running: {self.main_agent.job_scheduler.is_running()}")
            scheduled_jobs = self.main_agent.list_scheduled_jobs()
            logger.info(f"Number of scheduled jobs: {len(scheduled_jobs)}")
            for job in scheduled_jobs:
                logger.info(f"  - {job}")
    
    async def run(self) -> None:
        try:
            self._validate_environment()
            self._setup_signal_handlers()
            self._initialize_agent()
            
            logger.info("Talos daemon started successfully. Waiting for scheduled jobs...")
            logger.info("Send SIGTERM or SIGINT to gracefully shutdown the daemon.")
            
            await self.shutdown_event.wait()
            
        except Exception as e:
            logger.error(f"Error in daemon: {e}")
            sys.exit(1)


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    daemon = TalosDaemon()
    await daemon.run()


if __name__ == "__main__":
    asyncio.run(main())
