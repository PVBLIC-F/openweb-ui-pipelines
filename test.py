"""
OpenWeb UI Pipeline: File Upload Interceptor (Based on Official Scaffold)

This pipeline logs detailed information about file uploads in the chat interface.
It follows the exact structure of the official OpenWeb UI pipeline scaffold.
"""

import os
import logging
import json
from typing import List, Union, Generator, Iterator, Dict, Any, Optional
from pydantic import BaseModel

# Set up logging with a distinctive format for easy identification
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("file_upload_test")

class Pipeline:
    """
    Test pipeline that logs when files are uploaded in the chat interface.
    Based on the official OpenWeb UI pipeline scaffold.
    """
    
    class Valves(BaseModel):
        """
        Configuration valves for the pipeline.
        """
        # List target pipeline ids (models) that this filter will be connected to
        pipelines: List[str] = ["*"]  # Connect to all pipelines
        
        # Assign priority (lower number = higher priority)
        priority: int = 0
        
        # Add any other configuration options here if needed
        pass

    def __init__(self):
        """Initialize the pipeline"""
        # The name of the pipeline
        self.name = "File Upload Test Logger"
        
        # Log initialization
        logger.info("==================================================")
        logger.info("FILE UPLOAD TEST LOGGER PIPELINE INITIALIZED")
        logger.info("==================================================")

    async def on_startup(self):
        """Log when the pipeline starts"""
        logger.info("==================================================")
        logger.info("FILE UPLOAD TEST LOGGER PIPELINE STARTED")
        logger.info("==================================================")

    async def on_shutdown(self):
        """Log when the pipeline shuts down"""
        logger.info("==================================================")
        logger.info("FILE UPLOAD TEST LOGGER PIPELINE SHUTDOWN")
        logger.info("==================================================")
        
    async def on_valves_updated(self):
        """Called when valves are updated"""
        logger.info("==================================================")
        logger.info("VALVES UPDATED")
        logger.info("==================================================")

    async def inlet(self, body: dict, user: dict) -> dict:
        """
        Process incoming messages and log when files are detected.
        This is called before the OpenAI API request is made.
        """
        try:
            logger.info("==================================================")
            logger.info("INLET METHOD CALLED")
            logger.info("==================================================")
            
            # Log basic information about the body
            logger.info(f"Body keys: {list(body.keys())}")
            logger.info(f"User info: {user.get('id', 'unknown')}")
            
            # Extract messages from the body
            messages = body.get("messages", [])
            logger.info(f"Number of messages: {len(messages)}")
            
            # Check if there's a 'files' field directly in the body
            if "files" in body:
                files = body.get("files", [])
                logger.info("==================================================")
                logger.info(f"FILES FIELD FOUND IN BODY: {len(files)} files")
                for i, file in enumerate(files):
                    logger.info(f"File {i+1} info: {file}")
                logger.info("==================================================")
            
            # Look for file uploads in all messages
            for i, message in enumerate(messages):
                logger.info(f"Checking message {i+1} (role: {message.get('role', 'unknown')})")
                
                # Check if there's a 'files' field in the message
                if "files" in message:
                    files = message.get("files", [])
                    logger.info("==================================================")
                    logger.info(f"FILES FIELD FOUND IN MESSAGE {i+1}: {len(files)} files")
                    for j, file in enumerate(files):
                        logger.info(f"File {j+1} info: {file}")
                    logger.info("==================================================")
                
                # Get the content (might be a string or a list of content parts)
                content = message.get("content", "")
                
                # Log content type
                logger.info(f"Content type: {type(content).__name__}")
                
                # If content is a list, check each part for file data
                if isinstance(content, list):
                    logger.info(f"Content is a list with {len(content)} parts")
                    
                    for j, content_part in enumerate(content):
                        if isinstance(content_part, dict):
                            logger.info(f"Checking content part {j+1} (type: {content_part.get('type', 'unknown')})")
                            
                            # Check if this is a file attachment
                            if content_part.get("type") == "file":
                                file_name = content_part.get("name", "unknown_file")
                                mime_type = content_part.get("mime_type", "unknown_type")
                                
                                logger.info("==================================================")
                                logger.info(f"FILE PART DETECTED IN MESSAGE {i+1}, PART {j+1}!")
                                logger.info(f"File Name: {file_name}")
                                logger.info(f"MIME Type: {mime_type}")
                                logger.info("==================================================")
                                
                                # Log the structure of the file part
                                logger.info(f"File part structure: {content_part}")
                            
                            # Check if this is an image with a data URL
                            elif content_part.get("type") == "image_url":
                                image_url_data = content_part.get("image_url", {})
                                logger.info(f"Image URL data: {image_url_data}")
                                
                                image_url = image_url_data.get("url", "") if isinstance(image_url_data, dict) else ""
                                
                                # Check if it's a data URL
                                if image_url and isinstance(image_url, str) and image_url.startswith("data:"):
                                    # Extract MIME type if present
                                    mime_type = "image/unknown"
                                    if ";" in image_url:
                                        mime_part = image_url.split(";")[0]
                                        if mime_part.startswith("data:"):
                                            mime_type = mime_part[5:]
                                    
                                    logger.info("==================================================")
                                    logger.info(f"IMAGE URL DETECTED IN MESSAGE {i+1}, PART {j+1}!")
                                    logger.info(f"MIME Type: {mime_type}")
                                    logger.info("==================================================")
                elif isinstance(content, str):
                    # Log a preview of string content
                    preview = content[:100] + "..." if len(content) > 100 else content
                    logger.info(f"Content is a string: {preview}")
            
            # Return the body unchanged - we're just logging, not modifying
            logger.info("==================================================")
            logger.info("INLET METHOD COMPLETED - RETURNING UNMODIFIED BODY")
            logger.info("==================================================")
            return body
            
        except Exception as e:
            logger.error(f"Error in inlet method: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            # Return original body on error
            return body

    async def outlet(self, body: dict, user: dict) -> dict:
        """
        Process outgoing messages - log basic information.
        This is called after the OpenAI API response is completed.
        """
        try:
            logger.info("==================================================")
            logger.info("OUTLET METHOD CALLED")
            logger.info(f"Body keys: {list(body.keys())}")
            logger.info("==================================================")
        except Exception as e:
            logger.error(f"Error in outlet method: {str(e)}")
        
        return body
        
    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        """
        Custom pipeline processing - log information about the pipe call.
        This is where you can add custom pipelines like RAG.
        """
        try:
            logger.info("==================================================")
            logger.info("PIPE METHOD CALLED")
            logger.info(f"User message: {user_message[:100]}...")
            logger.info(f"Model ID: {model_id}")
            logger.info(f"Number of messages: {len(messages)}")
            logger.info(f"Body keys: {list(body.keys())}")
            
            # Check if this is a title generation request
            if body.get("title", False):
                logger.info("Title Generation Request")
                
            # Look for file uploads in messages
            for i, message in enumerate(messages):
                if message.get("role") == "user":
                    logger.info(f"Checking user message {i+1}")
                    
                    # Check if there's a 'files' field in the message
                    if "files" in message:
                        files = message.get("files", [])
                        logger.info("==================================================")
                        logger.info(f"FILES FIELD FOUND IN MESSAGE {i+1}: {len(files)} files")
                        for j, file in enumerate(files):
                            logger.info(f"File {j+1} info: {file}")
                        logger.info("==================================================")
                    
                    # Get the content (might be a string or a list of content parts)
                    content = message.get("content", "")
                    
                    # If content is a list, check each part for file data
                    if isinstance(content, list):
                        for j, content_part in enumerate(content):
                            if isinstance(content_part, dict):
                                # Check if this is a file attachment
                                if content_part.get("type") == "file":
                                    file_name = content_part.get("name", "unknown_file")
                                    mime_type = content_part.get("mime_type", "unknown_type")
                                    
                                    logger.info("==================================================")
                                    logger.info(f"FILE PART DETECTED IN PIPE METHOD!")
                                    logger.info(f"File Name: {file_name}")
                                    logger.info(f"MIME Type: {mime_type}")
                                    logger.info("==================================================")
            
            logger.info("==================================================")
            logger.info("PIPE METHOD COMPLETED")
            logger.info("==================================================")
        except Exception as e:
            logger.error(f"Error in pipe method: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
        
        # Return a response
        return f"File Upload Test Logger processed message: {user_message[:30]}..."
