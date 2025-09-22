"""
Multimodal Agent with Multiple Extraction Techniques
Supports native multimodality, extract to text, and multimodal tools
"""

import os
import sys
import json
import base64
import httpx
import asyncio
from typing import Dict, Any, List, Optional, Union, Generator, AsyncGenerator
from dataclasses import dataclass, field
from pathlib import Path
import mimetypes
from datetime import datetime

# Google Gemini imports
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# OpenAI imports
from openai import OpenAI, AsyncOpenAI

from config import Config, ExtractionMode, Provider, ModelConfig


@dataclass
class Message:
    """Unified message format"""
    role: str  # "system", "user", "assistant", "tool"
    content: Union[str, List[Dict[str, Any]]]
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        result = {"role": self.role, "content": self.content}
        if self.tool_calls:
            result["tool_calls"] = self.tool_calls
        if self.tool_call_id:
            result["tool_call_id"] = self.tool_call_id
        if self.name:
            result["name"] = self.name
        return result


@dataclass
class MultimodalContent:
    """Container for multimodal content"""
    type: str  # "pdf", "image", "audio"
    data: Optional[bytes] = None
    path: Optional[str] = None
    url: Optional[str] = None
    mime_type: Optional[str] = None
    extracted_text: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_bytes(self) -> bytes:
        """Get content as bytes"""
        if self.data:
            return self.data
        elif self.path:
            return Path(self.path).read_bytes()
        elif self.url:
            response = httpx.get(self.url)
            return response.content
        else:
            raise ValueError("No content source available")
            
    def get_base64(self) -> str:
        """Get content as base64 encoded string"""
        return base64.b64encode(self.get_bytes()).decode('utf-8')


class MultimodalTools:
    """Tools for multimodal content analysis"""
    
    def __init__(self, agent: 'MultimodalAgent'):
        self.agent = agent
        
    async def analyze_image(self, image_path: str, query: str) -> str:
        """Analyze an image with a specific query"""
        content = MultimodalContent(
            type="image",
            path=image_path,
            mime_type=mimetypes.guess_type(image_path)[0] or "image/jpeg"
        )
        
        # Use GPT-5 or Doubao for image analysis
        if self.agent.config.get_model_config(self.agent.current_model).provider == Provider.DOUBAO:
            return await self._analyze_with_doubao(content, query)
        else:
            return await self._analyze_with_openai(content, query)
            
    async def analyze_audio(self, audio_path: str, query: str) -> str:
        """Analyze audio with a specific query"""
        content = MultimodalContent(
            type="audio",
            path=audio_path,
            mime_type=mimetypes.guess_type(audio_path)[0] or "audio/mpeg"
        )
        
        # Use Gemini for audio analysis
        return await self._analyze_with_gemini_audio(content, query)
        
    async def analyze_pdf(self, pdf_path: str, query: str) -> str:
        """Analyze a PDF document with a specific query"""
        content = MultimodalContent(
            type="pdf",
            path=pdf_path,
            mime_type="application/pdf"
        )
        
        # Use Gemini for PDF analysis
        return await self._analyze_with_gemini_pdf(content, query)
        
    async def _analyze_with_openai(self, content: MultimodalContent, query: str) -> str:
        """Use OpenAI for content analysis"""
        client = AsyncOpenAI(api_key=self.agent.config.openai_api_key)
        
        messages = [{
            "role": "user",
            "content": [
                {"type": "text", "text": query},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{content.mime_type};base64,{content.get_base64()}"
                    }
                }
            ]
        }]
        
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=self.agent.config.temperature
        )
        
        return response.choices[0].message.content
        
    async def _analyze_with_doubao(self, content: MultimodalContent, query: str) -> str:
        """Use Doubao for content analysis"""
        client = AsyncOpenAI(
            api_key=self.agent.config.doubao_api_key,
            base_url=self.agent.config.models["doubao-1.6"].base_url
        )
        
        messages = [{
            "role": "user",
            "content": [
                {"type": "text", "text": query},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{content.mime_type};base64,{content.get_base64()}"
                    }
                }
            ]
        }]
        
        response = await client.chat.completions.create(
            model="Doubao-1.6",
            messages=messages,
            temperature=self.agent.config.temperature
        )
        
        return response.choices[0].message.content
        
    async def _analyze_with_gemini_audio(self, content: MultimodalContent, query: str) -> str:
        """Use Gemini for audio analysis"""
        genai.configure(api_key=self.agent.config.gemini_api_key)
        model = genai.GenerativeModel('gemini-2.5-pro')
        
        audio_data = content.get_bytes()
        response = model.generate_content([
            query,
            {"mime_type": content.mime_type, "data": audio_data}
        ])
        
        return response.text
        
    async def _analyze_with_gemini_pdf(self, content: MultimodalContent, query: str) -> str:
        """Use Gemini for PDF analysis"""
        genai.configure(api_key=self.agent.config.gemini_api_key)
        model = genai.GenerativeModel('gemini-2.5-pro')
        
        pdf_data = content.get_bytes()
        response = model.generate_content([
            {"mime_type": "application/pdf", "data": pdf_data},
            query
        ])
        
        return response.text


class MultimodalAgent:
    """Main agent class supporting multiple extraction modes"""
    
    def __init__(
        self,
        model: Optional[str] = None,
        mode: Optional[ExtractionMode] = None,
        enable_tools: bool = False
    ):
        self.config = Config()
        self.current_model = model or self.config.default_model
        self.extraction_mode = mode or self.config.default_mode
        self.enable_multimodal_tools = enable_tools
        
        # Conversation history
        self.conversation_history: List[Message] = []
        
        # Multimodal tools
        self.tools = MultimodalTools(self) if enable_tools else None
        
        # Tool definitions for OpenAI-style function calling
        self.tool_definitions = []
        if enable_tools:
            self.tool_definitions = [
                {
                    "type": "function",
                    "function": {
                        "name": "analyze_image",
                        "description": "Analyze an image with a specific query",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "image_path": {
                                    "type": "string",
                                    "description": "Path to the image file"
                                },
                                "query": {
                                    "type": "string",
                                    "description": "Question or analysis request about the image"
                                }
                            },
                            "required": ["image_path", "query"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "analyze_audio",
                        "description": "Analyze audio content with a specific query",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "audio_path": {
                                    "type": "string",
                                    "description": "Path to the audio file"
                                },
                                "query": {
                                    "type": "string",
                                    "description": "Question or analysis request about the audio"
                                }
                            },
                            "required": ["audio_path", "query"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "analyze_pdf",
                        "description": "Analyze a PDF document with a specific query",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "pdf_path": {
                                    "type": "string",
                                    "description": "Path to the PDF file"
                                },
                                "query": {
                                    "type": "string",
                                    "description": "Question or analysis request about the PDF"
                                }
                            },
                            "required": ["pdf_path", "query"]
                        }
                    }
                }
            ]
            
    def add_message(self, message: Message):
        """Add a message to conversation history"""
        self.conversation_history.append(message)
        
    async def process_multimodal_content(
        self,
        content: MultimodalContent,
        query: Optional[str] = None
    ) -> str:
        """Process multimodal content based on extraction mode"""
        
        if self.extraction_mode == ExtractionMode.NATIVE:
            return await self._process_native(content, query)
        elif self.extraction_mode == ExtractionMode.EXTRACT_TO_TEXT:
            return await self._extract_to_text(content, query)
        else:
            raise ValueError(f"Unknown extraction mode: {self.extraction_mode}")
            
    async def _process_native(self, content: MultimodalContent, query: Optional[str]) -> str:
        """Process using native multimodal capabilities"""
        model_config = self.config.get_model_config(self.current_model)
        
        if not model_config.supports_native_multimodal:
            raise ValueError(f"Model {self.current_model} doesn't support native multimodality")
            
        if model_config.provider == Provider.GEMINI:
            return await self._process_native_gemini(content, query)
        elif model_config.provider == Provider.OPENAI:
            return await self._process_native_openai(content, query)
        elif model_config.provider == Provider.DOUBAO:
            return await self._process_native_doubao(content, query)
        else:
            raise ValueError(f"Unknown provider: {model_config.provider}")
            
    async def _process_native_gemini(self, content: MultimodalContent, query: Optional[str]) -> str:
        """Process using Gemini's native multimodal API"""
        genai.configure(api_key=self.config.gemini_api_key)
        model = genai.GenerativeModel('gemini-2.5-pro')
        
        # Build prompt parts
        parts = []
        
        # Add the multimodal content
        content_bytes = content.get_bytes()
        if content.type == "pdf":
            parts.append({"mime_type": "application/pdf", "data": content_bytes})
        elif content.type == "image":
            parts.append({"mime_type": content.mime_type or "image/jpeg", "data": content_bytes})
        elif content.type == "audio":
            parts.append({"mime_type": content.mime_type or "audio/mpeg", "data": content_bytes})
            
        # Add the query
        if query:
            parts.append(query)
        else:
            parts.append(f"Please analyze this {content.type} content.")
            
        response = model.generate_content(parts)
        return response.text
        
    async def _process_native_openai(self, content: MultimodalContent, query: Optional[str]) -> str:
        """Process using OpenAI's native multimodal API"""
        client = AsyncOpenAI(api_key=self.config.openai_api_key)
        
        messages = []
        message_content = []
        
        if query:
            message_content.append({"type": "text", "text": query})
            
        # OpenAI primarily supports images natively
        if content.type == "image":
            message_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:{content.mime_type};base64,{content.get_base64()}"
                }
            })
        else:
            # For other types, we'll need to extract to text first
            extracted = await self._extract_single_content(content)
            message_content.append({"type": "text", "text": extracted})
            
        messages.append({"role": "user", "content": message_content})
        
        response = await client.chat.completions.create(
            model=self.current_model,
            messages=messages,
            temperature=self.config.temperature
        )
        
        return response.choices[0].message.content
        
    async def _process_native_doubao(self, content: MultimodalContent, query: Optional[str]) -> str:
        """Process using Doubao's native multimodal API"""
        client = AsyncOpenAI(
            api_key=self.config.doubao_api_key,
            base_url=self.config.models["doubao-1.6"].base_url
        )
        
        messages = []
        message_content = []
        
        if query:
            message_content.append({"type": "text", "text": query})
            
        # Doubao supports images natively
        if content.type == "image":
            message_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:{content.mime_type};base64,{content.get_base64()}"
                }
            })
        else:
            # For other types, extract to text first
            extracted = await self._extract_single_content(content)
            message_content.append({"type": "text", "text": extracted})
            
        messages.append({"role": "user", "content": message_content})
        
        response = await client.chat.completions.create(
            model="Doubao-1.6",
            messages=messages,
            temperature=self.config.temperature
        )
        
        return response.choices[0].message.content
        
    async def _extract_to_text(self, content: MultimodalContent, query: Optional[str]) -> str:
        """Extract multimodal content to text first"""
        extracted_text = await self._extract_single_content(content)
        content.extracted_text = extracted_text
        
        # Now process the query with extracted text
        if query:
            return await self._answer_with_context(extracted_text, query)
        else:
            return extracted_text
            
    async def _extract_single_content(self, content: MultimodalContent) -> str:
        """Extract a single piece of content to text"""
        if content.type == "pdf":
            return await self._extract_pdf_to_text(content)
        elif content.type == "image":
            return await self._extract_image_to_text(content)
        elif content.type == "audio":
            return await self._extract_audio_to_text(content)
        else:
            raise ValueError(f"Unknown content type: {content.type}")
            
    async def _extract_pdf_to_text(self, content: MultimodalContent) -> str:
        """Extract PDF to text using OCR"""
        # Option 1: Use Gemini for PDF extraction
        genai.configure(api_key=self.config.gemini_api_key)
        model = genai.GenerativeModel('gemini-2.5-pro')
        
        pdf_data = content.get_bytes()
        response = model.generate_content([
            {"mime_type": "application/pdf", "data": pdf_data},
            "Extract all text content from this PDF document, preserving structure and formatting."
        ])
        
        return response.text
        
    async def _extract_image_to_text(self, content: MultimodalContent) -> str:
        """Extract image to text description"""
        # Use GPT-4o or Doubao for image description
        if self.config.openai_api_key:
            client = AsyncOpenAI(api_key=self.config.openai_api_key)
            model = "gpt-4o"
        else:
            client = AsyncOpenAI(
                api_key=self.config.doubao_api_key,
                base_url=self.config.models["doubao-1.6"].base_url
            )
            model = "Doubao-1.6"
            
        messages = [{
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Describe this image in detail, including all text, objects, and contextual information."
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{content.mime_type};base64,{content.get_base64()}"
                    }
                }
            ]
        }]
        
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.3
        )
        
        return response.choices[0].message.content
        
    async def _extract_audio_to_text(self, content: MultimodalContent) -> str:
        """Extract audio to text transcript"""
        # Option 1: Use Whisper API
        if self.config.openai_api_key:
            client = AsyncOpenAI(api_key=self.config.openai_api_key)
            
            # Save audio temporarily for Whisper
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                tmp.write(content.get_bytes())
                tmp_path = tmp.name
                
            try:
                with open(tmp_path, "rb") as audio_file:
                    transcript = await client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file
                    )
                return transcript.text
            finally:
                os.unlink(tmp_path)
        else:
            # Option 2: Use Gemini for audio understanding
            genai.configure(api_key=self.config.gemini_api_key)
            model = genai.GenerativeModel('gemini-2.5-pro')
            
            audio_data = content.get_bytes()
            response = model.generate_content([
                "Transcribe this audio content completely and accurately.",
                {"mime_type": content.mime_type or "audio/mpeg", "data": audio_data}
            ])
            
            return response.text
            
    async def _answer_with_context(self, context: str, query: str) -> str:
        """Answer a query given extracted text context"""
        model_config = self.config.get_model_config(self.current_model)
        
        prompt = f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer:"
        
        if model_config.provider == Provider.GEMINI:
            genai.configure(api_key=self.config.gemini_api_key)
            model = genai.GenerativeModel(model_config.model_name)
            response = model.generate_content(prompt)
            return response.text
        else:
            # Use OpenAI-compatible API
            if model_config.provider == Provider.OPENAI:
                client = AsyncOpenAI(api_key=self.config.openai_api_key)
            else:  # Doubao
                client = AsyncOpenAI(
                    api_key=self.config.doubao_api_key,
                    base_url=model_config.base_url
                )
                
            response = await client.chat.completions.create(
                model=model_config.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.config.temperature
            )
            
            return response.choices[0].message.content
            
    async def chat(
        self,
        message: str,
        multimodal_content: Optional[MultimodalContent] = None,
        stream: bool = True
    ) -> AsyncGenerator[str, None]:
        """Main chat interface with streaming support"""
        
        # Add user message to history
        self.add_message(Message(role="user", content=message))
        
        # Process multimodal content if provided
        if multimodal_content:
            if self.extraction_mode == ExtractionMode.EXTRACT_TO_TEXT:
                # Extract to text and add to context
                extracted = await self._extract_single_content(multimodal_content)
                multimodal_content.extracted_text = extracted
                
                # Update message with extracted context
                enhanced_message = f"[Context from {multimodal_content.type}]:\n{extracted}\n\n{message}"
                self.conversation_history[-1].content = enhanced_message
                
        # Get response based on model
        model_config = self.config.get_model_config(self.current_model)
        
        if stream:
            async for chunk in self._stream_response(model_config):
                yield chunk
        else:
            response = await self._get_response(model_config)
            yield response
            
    async def _stream_response(self, model_config: ModelConfig) -> AsyncGenerator[str, None]:
        """Stream response from the model"""
        if model_config.provider == Provider.GEMINI:
            async for chunk in self._stream_gemini_response():
                yield chunk
        else:
            async for chunk in self._stream_openai_response(model_config):
                yield chunk
                
    async def _stream_gemini_response(self) -> AsyncGenerator[str, None]:
        """Stream response from Gemini"""
        genai.configure(api_key=self.config.gemini_api_key)
        model = genai.GenerativeModel(self.config.get_model_config(self.current_model).model_name)
        
        # Convert conversation history to Gemini format
        messages = []
        for msg in self.conversation_history:
            if msg.role == "user":
                messages.append({"role": "user", "parts": [msg.content]})
            elif msg.role == "assistant":
                messages.append({"role": "model", "parts": [msg.content]})
                
        response = model.generate_content(
            messages[-1]["parts"][0],
            stream=True
        )
        
        full_response = ""
        for chunk in response:
            if chunk.text:
                yield chunk.text
                full_response += chunk.text
                
        # Add assistant response to history
        self.add_message(Message(role="assistant", content=full_response))
        
    async def _stream_openai_response(self, model_config: ModelConfig) -> AsyncGenerator[str, None]:
        """Stream response from OpenAI-compatible API"""
        if model_config.provider == Provider.OPENAI:
            client = AsyncOpenAI(api_key=self.config.openai_api_key)
        else:  # Doubao
            client = AsyncOpenAI(
                api_key=self.config.doubao_api_key,
                base_url=model_config.base_url
            )
            
        # Convert conversation history to OpenAI format
        messages = [msg.to_dict() for msg in self.conversation_history]
        
        # Add tools if enabled
        kwargs = {
            "model": model_config.model_name,
            "messages": messages,
            "temperature": self.config.temperature,
            "stream": True
        }
        
        if self.enable_multimodal_tools and self.tool_definitions:
            kwargs["tools"] = self.tool_definitions
            kwargs["tool_choice"] = "auto"
            
        response = await client.chat.completions.create(**kwargs)
        
        full_response = ""
        tool_calls = []
        
        async for chunk in response:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                yield content
                full_response += content
                
            # Handle tool calls
            if chunk.choices[0].delta.tool_calls:
                for tool_call in chunk.choices[0].delta.tool_calls:
                    # Accumulate tool call information
                    if tool_call.index >= len(tool_calls):
                        tool_calls.append({
                            "id": tool_call.id,
                            "type": "function",
                            "function": {"name": "", "arguments": ""}
                        })
                    
                    if tool_call.function.name:
                        tool_calls[tool_call.index]["function"]["name"] = tool_call.function.name
                    if tool_call.function.arguments:
                        tool_calls[tool_call.index]["function"]["arguments"] += tool_call.function.arguments
                        
        # Process tool calls if any
        if tool_calls:
            # Add assistant message with tool calls
            self.add_message(Message(
                role="assistant",
                content=full_response or "",
                tool_calls=tool_calls
            ))
            
            # Execute tools
            for tool_call in tool_calls:
                tool_result = await self._execute_tool(tool_call)
                
                # Add tool result to history
                self.add_message(Message(
                    role="tool",
                    content=tool_result,
                    tool_call_id=tool_call["id"],
                    name=tool_call["function"]["name"]
                ))
                
                # Stream tool result
                yield f"\n[Tool: {tool_call['function']['name']}]\n{tool_result}\n"
                
            # Get final response after tool execution
            async for chunk in self._stream_openai_response(model_config):
                yield chunk
        else:
            # Add assistant response to history
            self.add_message(Message(role="assistant", content=full_response))
            
    async def _execute_tool(self, tool_call: Dict[str, Any]) -> str:
        """Execute a tool call"""
        function_name = tool_call["function"]["name"]
        arguments = json.loads(tool_call["function"]["arguments"])
        
        if function_name == "analyze_image":
            return await self.tools.analyze_image(
                arguments["image_path"],
                arguments["query"]
            )
        elif function_name == "analyze_audio":
            return await self.tools.analyze_audio(
                arguments["audio_path"],
                arguments["query"]
            )
        elif function_name == "analyze_pdf":
            return await self.tools.analyze_pdf(
                arguments["pdf_path"],
                arguments["query"]
            )
        else:
            return f"Unknown tool: {function_name}"
            
    async def _get_response(self, model_config: ModelConfig) -> str:
        """Get non-streaming response"""
        full_response = ""
        async for chunk in self._stream_response(model_config):
            full_response += chunk
        return full_response
        
    def reset_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []
        
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history in OpenAI format"""
        return [msg.to_dict() for msg in self.conversation_history]
