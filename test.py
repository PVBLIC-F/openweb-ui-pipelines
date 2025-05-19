"""
Minimal Test Pipeline for OpenWeb UI File Upload Interception
------------------------------------------------------------
This is an extremely minimal pipeline that only logs when the inlet method is called
and dumps the structure of the message to help debug file upload interception.
"""

import logging
import json
from typing import Dict, List, Optional, Any
from pydantic import BaseModel

# Set up logging with a distinctive format for easy identification
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("minimal_test")

class Pipeline:
    """
    Minimal test pipeline that just logs when inlet is called and dumps message structure.
    """
    
    class Valves(BaseModel):
        """
        Configuration valves for the pipeline.
        """
        # List target pipeline ids (models) that this filter will be connected to
        pipelines: List[str] = ["*"]  # Connect to all pipelines
        
        # Assign priority (lower number = higher priority)
        priority: int = 0

    def __init__(self):
        """Initialize the pipeline"""
        self.type = "filter"  # This is critical - must be "filter" for inlet/outlet
        self.name = "Minimal Test Pipeline"
        self.valves = self.Valves()
        logger.info("=" * 70)
        logger.info("MINIMAL TEST PIPELINE INITIALIZED")
        logger.info("=" * 70)

    async def on_startup(self):
        """Log when the pipeline starts"""
        logger.info("=" * 70)
        logger.info("MINIMAL TEST PIPELINE STARTED")
        logger.info("=" * 70)

    async def on_shutdown(self):
        """Log when the pipeline shuts down"""
        logger.info("=" * 70)
        logger.info("MINIMAL TEST PIPELINE SHUTDOWN")
        logger.info("=" * 70)

    def _safe_json(self, obj):
        """Convert object to JSON string safely, handling circular references"""
        try:
            return json.dumps(obj, default=str, indent=2)
        except:
            return str(obj)

    async def inlet(self, body: dict, user: Optional[dict] = None) -> dict:
        """
        Process incoming messages and log detailed structure for debugging.
        """
        try:
            logger.info("=" * 70)
            logger.info("INLET METHOD CALLED")
            logger.info(f"Body keys: {list(body.keys())}")
            
            # Log basic message info
            messages = body.get("messages", [])
            logger.info(f"Message count: {len(messages)}")
            
            # Get user ID and chat ID for tracking
            user_id = "unknown_user"
            if user:
                logger.info(f"User info: {self._safe_json(user)}")
                user_id = user.get("id", "unknown_user")
            
            chat_id = body.get("conversation_id", "unknown_chat")
            logger.info(f"Chat ID: {chat_id}")
            logger.info(f"User ID: {user_id}")
            
            # Check the most recent message in detail
            if messages:
                last_message = messages[-1]
                logger.info(f"Last message role: {last_message.get('role', 'unknown')}")
                
                # Check for files field
                files = last_message.get("files", [])
                if files:
                    logger.info(f"FILES FIELD FOUND with {len(files)} files")
                    for i, f in enumerate(files):
                        logger.info(f"File {i+1} keys: {list(f.keys())}")
                else:
                    logger.info("No files field found")
                
                # Check content structure
                content = last_message.get("content", "")
                if isinstance(content, list):
                    logger.info(f"Content is a list with {len(content)} items")
                    for i, part in enumerate(content):
                        if isinstance(part, dict):
                            logger.info(f"Content part {i+1} type: {part.get('type', 'unknown')}")
                            if part.get("type") == "file":
                                logger.info(f"FILE CONTENT PART FOUND: {part.get('name', 'unnamed')}")
                            elif part.get("type") == "image_url":
                                logger.info("IMAGE URL CONTENT PART FOUND")
                else:
                    logger.info("Content is not a list")
                
                # Log all message keys for debugging
                logger.info(f"All message keys: {list(last_message.keys())}")
            
            logger.info("=" * 70)
            
            # Return the body unchanged - we're just logging
            return body
            
        except Exception as e:
            logger.error(f"Error in minimal test pipeline: {str(e)}")
            logger.info("=" * 70)
            # Return original body on error
            return body

    async def outlet(self, body: dict, user: Optional[dict] = None) -> dict:
        """
        Process outgoing messages - just log that we were called.
        """
        logger.info("=" * 70)
        logger.info("OUTLET METHOD CALLED")
        logger.info("=" * 70)
        return body
