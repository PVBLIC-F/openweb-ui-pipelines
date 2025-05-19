""" 
title: File Upload Interceptor Pipeline
author: Manus
date: 2025-05-19
version: 1.0
license: MIT
description: A pipeline for intercepting file uploads in the chat interface and sending them to a custom RAG API.
requirements: requests
"""

from typing import List, Optional, Dict, Any
from schemas import OpenAIChatMessage
from pydantic import BaseModel
import os
import logging
import json
import base64
import tempfile
import requests
import uuid

# Set up logging with a distinctive format for easy identification
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("file_upload_interceptor")

class Pipeline:
    class Valves(BaseModel):
        # List target pipeline ids (models) that this filter will be connected to.
        # If you want to connect this filter to all pipelines, you can set pipelines to ["*"]
        # e.g. ["llama3:latest", "gpt-3.5-turbo"]
        pipelines: List[str] = ["*"]  # Connect to all pipelines
        
        # Assign a priority level to the filter pipeline.
        # The priority level determines the order in which the filter pipelines are executed.
        # The lower the number, the higher the priority.
        priority: int = 0
        
        # Custom RAG API endpoint
        rag_api_url: str = "http://localhost:8000/upload"
        
        # Enable dry run mode (log but don't process files)
        dry_run: bool = False

    def __init__(self):
        # Pipeline filters are only compatible with Open WebUI
        # You can think of filter pipeline as a middleware that can be used to edit the form data before it is sent to the OpenAI API.
        self.type = "filter"
        
        # The name of the pipeline
        self.name = "File Upload Interceptor"
        
        # Initialize valves
        self.valves = self.Valves(
            **{
                "pipelines": ["*"],  # Connect to all pipelines
            }
        )
        
        # Initialize HTTP client
        self.http_client = None
        
        # Log initialization
        logger.info("==================================================")
        logger.info("FILE UPLOAD INTERCEPTOR PIPELINE INITIALIZED")
        logger.info("==================================================")

    async def on_startup(self):
        """Log when the pipeline starts"""
        logger.info("==================================================")
        logger.info("FILE UPLOAD INTERCEPTOR PIPELINE STARTED")
        logger.info("==================================================")
        
        # Initialize HTTP client if needed
        # self.http_client = httpx.AsyncClient(timeout=10.0)

    async def on_shutdown(self):
        """Log when the pipeline shuts down"""
        logger.info("==================================================")
        logger.info("FILE UPLOAD INTERCEPTOR PIPELINE SHUTDOWN")
        logger.info("==================================================")
        
        # Close HTTP client if needed
        # if self.http_client:
        #     await self.http_client.aclose()
        
    async def on_valves_updated(self):
        """Called when valves are updated"""
        logger.info("==================================================")
        logger.info("VALVES UPDATED")
        logger.info(f"RAG API URL: {self.valves.rag_api_url}")
        logger.info(f"Dry Run: {self.valves.dry_run}")
        logger.info("==================================================")

    def _extract_file_from_message(self, message):
        """
        Extract file data from a message if present.
        Returns (file_found, file_data, file_name, mime_type)
        """
        content = message.get("content", [])
        
        # Handle different message content formats
        if isinstance(content, str):
            # No files in plain text messages
            return False, None, None, None
            
        if isinstance(content, list):
            # Modern format with content parts
            for part in content:
                # Check for file type
                if part.get("type") == "file":
                    logger.info(f"Found file part: {part}")
                    return (
                        True, 
                        part.get("file_data", {}), 
                        part.get("name", "uploaded_file"),
                        part.get("mime_type", "application/octet-stream")
                    )
                    
                # Check for image type (which might be a document)
                if part.get("type") == "image_url":
                    image_url = part.get("image_url", {})
                    if isinstance(image_url, dict) and "url" in image_url:
                        url = image_url["url"]
                        # Check if it's a data URL
                        if url.startswith("data:"):
                            mime_type = "image/unknown"
                            if ";" in url:
                                mime_part = url.split(";")[0]
                                if ":" in mime_part:
                                    mime_type = mime_part.split(":")[1]
                            
                            logger.info(f"Found image data URL with mime type: {mime_type}")
                            return True, url, "image_upload", mime_type
        
        # Check if there's a 'files' field in the message
        if "files" in message:
            files = message.get("files", [])
            if files and len(files) > 0:
                file = files[0]  # Take the first file
                logger.info(f"Found file in 'files' field: {file}")
                return True, file, file.get("name", "uploaded_file"), file.get("mime_type", "application/octet-stream")
        
        return False, None, None, None

    async def inlet(self, body: dict, user: Optional[dict] = None) -> dict:
        """
        This filter is applied to the form data before it is sent to the OpenAI API.
        It intercepts file uploads and sends them to the custom RAG API.
        """
        try:
            logger.info("==================================================")
            logger.info("INLET METHOD CALLED - CHECKING FOR FILES")
            logger.info("==================================================")
            
            # Extract messages from the body
            messages = body.get("messages", [])
            if not messages:
                return body
                
            # Get user ID and chat ID for tracking
            user_id = user.get("id", "unknown_user") if user else "unknown_user"
            chat_id = body.get("conversation_id", str(uuid.uuid4()))
            
            logger.info(f"User ID: {user_id}")
            logger.info(f"Chat ID: {chat_id}")
            
            # Look for file uploads in the most recent user message
            for i in range(len(messages) - 1, -1, -1):
                message = messages[i]
                
                # Only process user messages
                if message.get("role") != "user":
                    continue
                    
                # Check if this message contains file data
                file_found, file_data, file_name, mime_type = self._extract_file_from_message(message)
                
                if file_found and file_data:
                    logger.info(f"Intercepted file upload: {file_name} ({mime_type})")
                    
                    # If dry run is enabled, just log and return
                    if self.valves.dry_run:
                        logger.info("DRY RUN MODE: Skipping file processing")
                        return body
                    
                    # Process the file
                    try:
                        # Save file to temporary location
                        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_name)[1]) as temp:
                            # Handle different file data formats
                            if isinstance(file_data, str) and file_data.startswith("data:"):
                                # Extract base64 data from data URL
                                if ";base64," in file_data:
                                    _, b64data = file_data.split(";base64,")
                                    binary_data = base64.b64decode(b64data)
                                    temp.write(binary_data)
                                    logger.info(f"Decoded base64 data URL, size: {len(binary_data)} bytes")
                                else:
                                    logger.info(f"Unsupported data URL format (not base64)")
                                    continue
                            elif isinstance(file_data, dict) and "bytes" in file_data:
                                # Handle bytes format
                                binary_data = base64.b64decode(file_data["bytes"])
                                temp.write(binary_data)
                                logger.info(f"Decoded bytes data, size: {len(binary_data)} bytes")
                            else:
                                logger.info(f"Unsupported file data format: {type(file_data)}")
                                continue
                                
                            temp_path = temp.name
                            
                        logger.info(f"Saved file to temporary location: {temp_path}")
                        
                        # Send the file to the custom RAG API
                        logger.info(f"Sending file to RAG API: {self.valves.rag_api_url}")
                        
                        with open(temp_path, "rb") as f:
                            files = {"file": (file_name, f, mime_type)}
                            data = {"chat_id": chat_id, "user_id": user_id}
                            
                            response = requests.post(
                                self.valves.rag_api_url,
                                files=files,
                                data=data
                            )
                            
                            if response.status_code == 200:
                                result = response.json()
                                logger.info(f"RAG API response: {result}")
                            else:
                                logger.error(f"RAG API error: {response.status_code} - {response.text}")
                        
                        # Clean up temp file
                        os.unlink(temp_path)
                        logger.info(f"Cleaned up temporary file")
                        
                    except Exception as e:
                        logger.error(f"Error processing file: {str(e)}")
                        import traceback
                        logger.error(traceback.format_exc())
                    
                    # We found and processed a file, no need to check earlier messages
                    break
            
            # Return the body unchanged
            return body
            
        except Exception as e:
            logger.error(f"Error in inlet method: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            # Return original body on error
            return body

    async def outlet(self, body: dict, user: Optional[dict] = None) -> dict:
        """
        This filter is applied to the response after it is sent from the OpenAI API.
        We don't need to modify the response, so we just return it unchanged.
        """
        return body
