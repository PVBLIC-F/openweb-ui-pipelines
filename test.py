"""
OpenWeb UI Pipeline: File Upload Interceptor (Enhanced Test Version)
Logs all incoming message content, not just file/image types, for deep debugging.
"""

import os
import logging
import uuid
import json
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("file_upload_test")

class Pipeline:
    class Valves(BaseModel):
        pipelines: List[str] = ["*"]
        priority: int = 0

    def __init__(self):
        self.type = "filter"
        self.name = "File Upload Deep Logger"
        self.valves = self.Valves()

    async def on_startup(self):
        logger.info("=== FILE UPLOAD DEEP LOGGER PIPELINE STARTED ===")

    async def on_shutdown(self):
        logger.info("=== FILE UPLOAD DEEP LOGGER PIPELINE SHUTDOWN ===")

    async def inlet(self, body: dict, user: Optional[dict] = None) -> dict:
        try:
            messages = body.get("messages", [])
            if not messages:
                logger.info("No messages found in body.")
                return body

            user_id = user.get("id") if user else "unknown_user"
            chat_id = body.get("conversation_id", str(uuid.uuid4()))
            logger.info("######## NEW INLET CALL ########")
            logger.info(f"User: {user_id}, Chat: {chat_id}")
            logger.info("Full messages:")
            logger.info(json.dumps(messages, indent=2, default=str))

            # Go over each message (especially the most recent user one)
            for i in range(len(messages) - 1, -1, -1):
                message = messages[i]
                if message.get("role") != "user":
                    continue
                content = message.get("content", "")
                logger.info(f"Message {i} USER CONTENT: {json.dumps(content, indent=2, default=str)}")

                # If content is a list (multipart)
                if isinstance(content, list):
                    for part in content:
                        part_type = part.get("type")
                        logger.info(f"Content part type: {part_type}")
                        if part_type == "file":
                            logger.info("------ FILE CONTENT PART DETECTED ------")
                            logger.info(json.dumps(part, indent=2, default=str))
                        elif part_type == "image_url":
                            logger.info("------ IMAGE CONTENT PART DETECTED ------")
                            logger.info(json.dumps(part, indent=2, default=str))
                        elif part_type == "text":
                            logger.info("------ TEXT CONTENT PART ------")
                            logger.info(json.dumps(part, indent=2, default=str))
                        else:
                            logger.info("------ OTHER CONTENT PART ------")
                            logger.info(json.dumps(part, indent=2, default=str))
                else:
                    # Not a list: likely inlined string (plaintext)
                    logger.info("------ CONTENT IS INLINE TEXT ------")
                    logger.info(f"{content}")
                break  # Only newest user message
            return body
        except Exception as e:
            logger.error(f"Error in test logger: {str(e)}")
            return body

    async def outlet(self, body: dict, user: Optional[dict] = None) -> dict:
        return body
