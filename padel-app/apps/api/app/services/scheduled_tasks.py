"""
Scheduled tasks for automatic tournament and game expiration
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.database import get_db
from app.services.game_expiration_service import game_expiration_service
from app.services.tournament_expiration_service import tournament_expiration_service

logger = logging.getLogger(__name__)


class ScheduledTasksService:
    """
    Service to handle scheduled background tasks for expiration
    """
    
    def __init__(self):
        self.is_running = False
        self.task_handle: Optional[asyncio.Task] = None
    
    async def start_scheduled_tasks(self, interval_minutes: int = 60):
        """
        Start the scheduled tasks background loop
        
        Args:
            interval_minutes: How often to run expiration tasks (default: 60 minutes)
        """
        if self.is_running:
            logger.warning("Scheduled tasks are already running")
            return
        
        self.is_running = True
        logger.info(f"Starting scheduled tasks with {interval_minutes} minute interval")
        
        self.task_handle = asyncio.create_task(self._run_scheduled_loop(interval_minutes))
    
    async def stop_scheduled_tasks(self):
        """Stop the scheduled tasks background loop"""
        if not self.is_running:
            return
        
        self.is_running = False
        if self.task_handle:
            self.task_handle.cancel()
            try:
                await self.task_handle
            except asyncio.CancelledError:
                pass
        
        logger.info("Stopped scheduled tasks")
    
    async def _run_scheduled_loop(self, interval_minutes: int):
        """Internal method to run the scheduled tasks loop"""
        try:
            while self.is_running:
                try:
                    await self._run_expiration_tasks()
                except Exception as e:
                    logger.error(f"Error in scheduled expiration tasks: {e}")
                
                # Wait for the next iteration
                await asyncio.sleep(interval_minutes * 60)
        except asyncio.CancelledError:
            logger.info("Scheduled tasks loop cancelled")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in scheduled tasks loop: {e}")
            self.is_running = False
    
    async def _run_expiration_tasks(self):
        """Run the expiration tasks"""
        try:
            # Get database session
            db = next(get_db())
            
            logger.info("Running scheduled expiration tasks")
            
            # Run tournament expiration
            tournament_result = tournament_expiration_service.expire_past_tournaments(db)
            if tournament_result["success"]:
                logger.info(f"Tournament expiration completed: {tournament_result['total_processed']} tournaments processed")
            else:
                logger.error(f"Tournament expiration failed: {tournament_result.get('error')}")
            
            # Run game expiration
            try:
                expired_game_ids = game_expiration_service.expire_past_games(db)
                logger.info(f"Game expiration completed: {len(expired_game_ids)} games expired")
            except Exception as e:
                logger.error(f"Game expiration failed: {e}")
            
            # Close database session
            db.close()
            
        except Exception as e:
            logger.error(f"Error in expiration tasks: {e}")
    
    async def run_expiration_tasks_now(self):
        """Run expiration tasks immediately (for testing/manual trigger)"""
        await self._run_expiration_tasks()


# Global instance
scheduled_tasks_service = ScheduledTasksService()


# FastAPI startup/shutdown event handlers
async def startup_scheduled_tasks():
    """Start scheduled tasks on application startup"""
    try:
        # Start with 1 hour interval (adjust as needed)
        await scheduled_tasks_service.start_scheduled_tasks(interval_minutes=60)
        logger.info("Scheduled tasks started successfully")
    except Exception as e:
        logger.error(f"Failed to start scheduled tasks: {e}")


async def shutdown_scheduled_tasks():
    """Stop scheduled tasks on application shutdown"""
    try:
        await scheduled_tasks_service.stop_scheduled_tasks()
        logger.info("Scheduled tasks stopped successfully")
    except Exception as e:
        logger.error(f"Failed to stop scheduled tasks: {e}")


# Manual trigger endpoint function
async def trigger_expiration_tasks_manually():
    """Manually trigger expiration tasks (for API endpoints)"""
    try:
        await scheduled_tasks_service.run_expiration_tasks_now()
        return {"success": True, "message": "Expiration tasks completed successfully"}
    except Exception as e:
        logger.error(f"Manual expiration tasks failed: {e}")
        return {"success": False, "error": str(e)}