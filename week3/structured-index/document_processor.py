"""
Document processor for handling various file formats.
Specializes in processing technical documentation like Intel manuals.
"""

import re
from pathlib import Path
from typing import List, Optional, Dict, Any
import pypdf
import pdfplumber
from bs4 import BeautifulSoup
import markdown
from loguru import logger
import asyncio
import aiofiles


class DocumentProcessor:
    """Process various document formats into text for indexing."""
    
    def __init__(self):
        self.supported_formats = {
            '.pdf': self.process_pdf,
            '.txt': self.process_text,
            '.md': self.process_markdown,
            '.html': self.process_html
        }
        logger.info("Initialized document processor")
    
    async def process_file(self, file_path: Path) -> str:
        """Process a file based on its extension."""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        ext = file_path.suffix.lower()
        
        if ext not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {ext}")
        
        processor = self.supported_formats[ext]
        
        # Run processor (some are async, some are sync)
        if asyncio.iscoroutinefunction(processor):
            return await processor(file_path)
        else:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, processor, file_path)
    
    def process_pdf(self, file_path: Path) -> str:
        """
        Process PDF files with special handling for technical documentation.
        Optimized for Intel manuals with complex formatting.
        """
        logger.info(f"Processing PDF: {file_path}")
        
        try:
            # Try pdfplumber first for better table extraction
            return self._process_pdf_with_pdfplumber(file_path)
        except Exception as e:
            logger.warning(f"pdfplumber failed, falling back to pypdf: {e}")
            return self._process_pdf_with_pypdf(file_path)
    
    def _process_pdf_with_pdfplumber(self, file_path: Path) -> str:
        """Process PDF using pdfplumber for better structure preservation."""
        text_content = []
        
        with pdfplumber.open(file_path) as pdf:
            total_pages = len(pdf.pages)
            logger.info(f"Processing {total_pages} pages...")
            
            for i, page in enumerate(pdf.pages):
                if i % 100 == 0:
                    logger.info(f"Processing page {i}/{total_pages}")
                
                # Extract text
                page_text = page.extract_text()
                if page_text:
                    # Clean up the text
                    page_text = self._clean_pdf_text(page_text)
                    text_content.append(page_text)
                
                # Extract tables if present
                tables = page.extract_tables()
                for table in tables:
                    if table:
                        # Convert table to structured text
                        table_text = self._format_table(table)
                        if table_text:
                            text_content.append(table_text)
        
        return "\n\n".join(text_content)
    
    def _process_pdf_with_pypdf(self, file_path: Path) -> str:
        """Fallback PDF processing using pypdf."""
        text_content = []
        
        with open(file_path, 'rb') as file:
            reader = pypdf.PdfReader(file)
            total_pages = len(reader.pages)
            logger.info(f"Processing {total_pages} pages with pypdf...")
            
            for i, page in enumerate(reader.pages):
                if i % 100 == 0:
                    logger.info(f"Processing page {i}/{total_pages}")
                
                text = page.extract_text()
                if text:
                    text = self._clean_pdf_text(text)
                    text_content.append(text)
        
        return "\n\n".join(text_content)
    
    def _clean_pdf_text(self, text: str) -> str:
        """Clean extracted PDF text."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix common PDF extraction issues
        text = re.sub(r'(\w)-\s+(\w)', r'\1\2', text)  # Fix hyphenated words
        text = re.sub(r'\s*\n\s*', '\n', text)  # Clean up newlines
        
        # Remove page numbers and headers (common in Intel manuals)
        text = re.sub(r'^[\d\s]*Intel.*?Manual.*?\n', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\d+-\d+\s*$', '', text, flags=re.MULTILINE)
        
        # Extract instruction definitions (Intel manual specific)
        text = self._extract_intel_instructions(text)
        
        return text.strip()
    
    def _extract_intel_instructions(self, text: str) -> str:
        """Extract and format Intel x86/x64 instructions."""
        # Pattern for Intel instruction format
        instruction_pattern = r'([A-Z]{2,}[A-Z0-9]*)\s*[-—]\s*([^\n]+)'
        
        # Find all instruction definitions
        matches = re.finditer(instruction_pattern, text)
        
        formatted_parts = []
        last_end = 0
        
        for match in matches:
            # Add text before the match
            formatted_parts.append(text[last_end:match.start()])
            
            # Format the instruction
            instruction = match.group(1)
            description = match.group(2)
            formatted_parts.append(f"\n**{instruction}**: {description}")
            
            last_end = match.end()
        
        # Add remaining text
        formatted_parts.append(text[last_end:])
        
        return ''.join(formatted_parts)
    
    def _format_table(self, table: List[List]) -> str:
        """Format a table into structured text."""
        if not table or not table[0]:
            return ""
        
        formatted = []
        
        # Assume first row is header
        headers = table[0]
        formatted.append("Table: " + " | ".join(str(h) for h in headers if h))
        
        # Format data rows
        for row in table[1:]:
            if row and any(cell for cell in row):
                formatted.append("  " + " | ".join(str(cell) if cell else "-" for cell in row))
        
        return "\n".join(formatted)
    
    async def process_text(self, file_path: Path) -> str:
        """Process plain text files."""
        logger.info(f"Processing text file: {file_path}")
        
        async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = await f.read()
        
        return content
    
    def process_markdown(self, file_path: Path) -> str:
        """Process Markdown files."""
        logger.info(f"Processing Markdown file: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Convert Markdown to plain text
        html = markdown.markdown(content)
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text()
        
        return text
    
    def process_html(self, file_path: Path) -> str:
        """Process HTML files."""
        logger.info(f"Processing HTML file: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Remove script and style elements
        for element in soup(['script', 'style']):
            element.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def extract_sections(self, text: str, section_pattern: Optional[str] = None) -> Dict[str, str]:
        """
        Extract sections from text based on patterns.
        Useful for structured documents like Intel manuals.
        """
        if section_pattern is None:
            # Default pattern for sections like "Chapter 1", "Section 2.3", etc.
            section_pattern = r'^(Chapter|Section|Part|\d+\.)\s+[\d\w\.]+.*$'
        
        sections = {}
        current_section = "Introduction"
        current_content = []
        
        for line in text.split('\n'):
            if re.match(section_pattern, line, re.IGNORECASE):
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content)
                
                # Start new section
                current_section = line.strip()
                current_content = []
            else:
                current_content.append(line)
        
        # Save last section
        if current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def extract_code_blocks(self, text: str) -> List[str]:
        """Extract code blocks or instruction examples from text."""
        code_blocks = []
        
        # Pattern for code blocks (various formats)
        patterns = [
            r'```[\s\S]*?```',  # Markdown code blocks
            r'<code>[\s\S]*?</code>',  # HTML code blocks
            r'^\s{4,}.*$',  # Indented code blocks
            r'^\t+.*$',  # Tab-indented blocks
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.MULTILINE)
            for match in matches:
                code_blocks.append(match.group(0))
        
        return code_blocks
    
    def extract_intel_opcodes(self, text: str) -> List[Dict[str, str]]:
        """
        Extract Intel instruction opcodes and their descriptions.
        Specific to Intel architecture manuals.
        """
        opcodes = []
        
        # Pattern for Intel opcode format
        opcode_pattern = r'([0-9A-F]{2}(?:\s+[0-9A-F]{2})*)\s+(/[0-7]|/r)?\s+([A-Z]+[A-Z0-9]*)\s+([^\n]+)'
        
        matches = re.finditer(opcode_pattern, text)
        for match in matches:
            opcodes.append({
                'opcode': match.group(1),
                'mod': match.group(2) or '',
                'instruction': match.group(3),
                'description': match.group(4).strip()
            })
        
        return opcodes
