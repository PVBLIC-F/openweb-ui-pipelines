"""
OpenWeb UI Pipeline: File Upload Interceptor (Test Version)

This simplified pipeline only logs when files are uploaded in the chat interface.
It's designed for testing file upload detection without any processing.
"""

import os
import logging
import uuid
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

# Set up logging with a distinctive format for easy identification
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("file_upload_test")

class Pipeline:
    """
    Test pipeline that only logs when files are uploaded in the chat interface.
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
        self.type = "filter"
        self.name = "File Upload Test Logger"
        self.valves = self.Valves()

    async def on_startup(self):
        """Log when the pipeline starts"""
        logger.info("========================================")
        logger.info("FILE UPLOAD TEST LOGGER PIPELINE STARTED")
        logger.info("========================================")

    async def on_shutdown(self):
        """Log when the pipeline shuts down"""
        logger.info("=========================================")
        logger.info("FILE UPLOAD TEST LOGGER PIPELINE SHUTDOWN")
        logger.info("=========================================")

    async def inlet(self, body: dict, user: Optional[dict] = None) -> dict:
        """
        Process incoming messages and log when files are detected.
        """
        try:
            # Extract messages from the body
            messages = body.get("messages", [])
            if not messages:
                return body
                
            # Get user ID and chat ID for tracking
            user_id = user.get("id") if user else "unknown_user"
            chat_id = body.get("conversation_id", str(uuid.uuid4()))
            
            # Look for file uploads in the most recent user message
            for i in range(len(messages) - 1, -1, -1):
                message = messages[i]
                
                # Only process user messages
                if message.get("role") != "user":
                    continue
                    
                # Get the content (might be a string or a list of content parts)
                content = message.get("content", "")
                
                # If content is a list, check each part for file data
                if isinstance(content, list):
                    for content_part in content:
                        # Check if this is a file attachment
                        if content_part.get("type") == "file":
                            file_name = content_part.get("name", "unknown_file")
                            mime_type = content_part.get("mime_type", "unknown_type")
                            
                            logger.info("====================================")
                            logger.info("FILE UPLOAD DETECTED!")
                            logger.info(f"Chat ID: {chat_id}")
                            logger.info(f"User ID: {user_id}")
                            logger.info(f"File Name: {file_name}")
                            logger.info(f"MIME Type: {mime_type}")
                            logger.info("====================================")
                            
                            # We found a file, no need to check further
                            break
                        
                        # Check if this is an image with a data URL
                        elif content_part.get("type") == "image_url":
                            image_url = content_part.get("image_url", {}).get("url", "")
                            
                            # Check if it's a data URL
                            if image_url and image_url.startswith("data:"):
                                # Extract MIME type if present
                                mime_type = "image/unknown"
                                if ";" in image_url:
                                    mime_part = image_url.split(";")[0]
                                    if mime_part.startswith("data:"):
                                        mime_type = mime_part[5:]
                                
                                logger.info("====================================")
                                logger.info("IMAGE UPLOAD DETECTED!")
                                logger.info(f"Chat ID: {chat_id}")
                                logger.info(f"User ID: {user_id}")
                                logger.info(f"MIME Type: {mime_type}")
                                logger.info("====================================")
                                
                                # We found an image, no need to check further
                                break
                
                # We processed a user message, no need to check earlier messages
                break
            
            # Return the body unchanged - we're just logging, not modifying
            return body
            
        except Exception as e:
            logger.error(f"Error in test logger: {str(e)}")
            # Return original body on error
            return body

    async def outlet(self, body: dict, user: Optional[dict] = None) -> dict:
        """
        Process outgoing messages - we don't need to do anything here.
        """
        return body
