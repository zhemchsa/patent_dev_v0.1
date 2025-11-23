"""
Text Chunking Utilities for Patent Processing

This module provides various text chunking strategies for processing patent documents,
optimized for vector embeddings and semantic search.
"""

from typing import List, Dict, Optional, Union, Tuple
import re
from dataclasses import dataclass
import tiktoken

@dataclass
class TextChunk:
    """Represents a chunk of text with metadata"""
    content: str
    start_index: int
    end_index: int
    chunk_id: str
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class PatentChunker:
    """Main class for chunking patent documents"""
    
    def __init__(self, chunk_size: int = 1000, overlap: int = 200, encoding_name: str = "cl100k_base"):
        """
        Initialize the patent chunker
        
        Args:
            chunk_size: Maximum tokens per chunk
            overlap: Number of overlapping tokens between chunks
            encoding_name: Tiktoken encoding name for token counting
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.encoding = tiktoken.get_encoding(encoding_name)
        
    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in text"""
        return len(self.encoding.encode(text))
    
    def chunk_by_tokens(self, text: str, document_id: str = None) -> List[TextChunk]:
        """
        Chunk text based on token count with overlapping windows
        
        Args:
            text: Input text to chunk
            document_id: Optional document identifier
            
        Returns:
            List of TextChunk objects
        """
        if not text.strip():
            return []
        
        tokens = self.encoding.encode(text)
        chunks = []
        
        start_idx = 0
        chunk_num = 0
        
        while start_idx < len(tokens):
            # Calculate end index for this chunk
            end_idx = min(start_idx + self.chunk_size, len(tokens))
            
            # Extract tokens for this chunk
            chunk_tokens = tokens[start_idx:end_idx]
            chunk_text = self.encoding.decode(chunk_tokens)
            
            # Find character positions in original text
            char_start = len(self.encoding.decode(tokens[:start_idx]))
            char_end = len(self.encoding.decode(tokens[:end_idx]))
            
            # Create chunk
            chunk_id = f"{document_id}_chunk_{chunk_num}" if document_id else f"chunk_{chunk_num}"
            
            chunk = TextChunk(
                content=chunk_text.strip(),
                start_index=char_start,
                end_index=char_end,
                chunk_id=chunk_id,
                metadata={
                    'token_count': len(chunk_tokens),
                    'chunk_number': chunk_num,
                    'document_id': document_id
                }
            )
            
            chunks.append(chunk)
            
            # Move start index forward, accounting for overlap
            if end_idx >= len(tokens):
                break
                
            start_idx = end_idx - self.overlap
            chunk_num += 1
        
        return chunks
    
    def chunk_by_sections(self, patent_text: str, document_id: str = None) -> List[TextChunk]:
        """
        Chunk patent text by logical sections (abstract, claims, description, etc.)
        
        Args:
            patent_text: Full patent text
            document_id: Optional document identifier
            
        Returns:
            List of TextChunk objects for each section
        """
        sections = self._extract_patent_sections(patent_text)
        chunks = []
        
        for section_name, section_text in sections.items():
            if not section_text.strip():
                continue
                
            # If section is small enough, keep as single chunk
            if self.count_tokens(section_text) <= self.chunk_size:
                chunk_id = f"{document_id}_{section_name}" if document_id else section_name
                
                chunk = TextChunk(
                    content=section_text.strip(),
                    start_index=0,
                    end_index=len(section_text),
                    chunk_id=chunk_id,
                    metadata={
                        'section_type': section_name,
                        'token_count': self.count_tokens(section_text),
                        'document_id': document_id
                    }
                )
                chunks.append(chunk)
            else:
                # Split large sections into smaller chunks
                section_chunks = self.chunk_by_tokens(section_text, f"{document_id}_{section_name}")
                
                # Add section metadata to each chunk
                for chunk in section_chunks:
                    chunk.metadata['section_type'] = section_name
                    
                chunks.extend(section_chunks)
        
        return chunks
    
    def chunk_by_paragraphs(self, text: str, document_id: str = None) -> List[TextChunk]:
        """
        Chunk text by paragraphs, combining small paragraphs and splitting large ones
        
        Args:
            text: Input text to chunk
            document_id: Optional document identifier
            
        Returns:
            List of TextChunk objects
        """
        paragraphs = re.split(r'\n\s*\n', text)
        chunks = []
        current_chunk = ""
        current_start = 0
        chunk_num = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            para_tokens = self.count_tokens(para)
            current_tokens = self.count_tokens(current_chunk)
            
            # If adding this paragraph would exceed chunk size
            if current_tokens + para_tokens > self.chunk_size and current_chunk:
                # Save current chunk
                chunk_id = f"{document_id}_para_{chunk_num}" if document_id else f"para_{chunk_num}"
                
                chunk = TextChunk(
                    content=current_chunk.strip(),
                    start_index=current_start,
                    end_index=current_start + len(current_chunk),
                    chunk_id=chunk_id,
                    metadata={
                        'token_count': current_tokens,
                        'chunk_number': chunk_num,
                        'document_id': document_id,
                        'chunk_type': 'paragraph_based'
                    }
                )
                chunks.append(chunk)
                
                # Start new chunk
                current_chunk = para
                current_start = current_start + len(chunks[-1].content) if chunks else 0
                chunk_num += 1
                
            else:
                # Add paragraph to current chunk
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
            
            # If this single paragraph is too large, split it
            if self.count_tokens(current_chunk) > self.chunk_size:
                # Split the large paragraph using token-based chunking
                large_chunks = self.chunk_by_tokens(current_chunk, f"{document_id}_large_para_{chunk_num}")
                chunks.extend(large_chunks)
                
                current_chunk = ""
                chunk_num += len(large_chunks)
        
        # Add final chunk if any content remains
        if current_chunk.strip():
            chunk_id = f"{document_id}_para_{chunk_num}" if document_id else f"para_{chunk_num}"
            
            chunk = TextChunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                chunk_id=chunk_id,
                metadata={
                    'token_count': self.count_tokens(current_chunk),
                    'chunk_number': chunk_num,
                    'document_id': document_id,
                    'chunk_type': 'paragraph_based'
                }
            )
            chunks.append(chunk)
        
        return chunks
    
    def _extract_patent_sections(self, patent_text: str) -> Dict[str, str]:
        """
        Extract different sections from patent text
        
        Args:
            patent_text: Full patent document text
            
        Returns:
            Dictionary mapping section names to section content
        """
        sections = {
            'abstract': '',
            'background': '',
            'summary': '',
            'description': '',
            'claims': '',
            'other': ''
        }
        
        # Define patterns for common patent sections
        patterns = {
            'abstract': r'(?i)(?:abstract|summary of the invention)[\s\n]*(.*?)(?=\n(?:background|field|technical field|summary|brief description|detailed description|claims|what is claimed)|\Z)',
            'background': r'(?i)(?:background|field of the invention|technical field)[\s\n]*(.*?)(?=\n(?:summary|brief description|detailed description|claims|abstract)|\Z)',
            'summary': r'(?i)(?:summary|brief summary|summary of the invention)[\s\n]*(.*?)(?=\n(?:brief description|detailed description|claims|background)|\Z)',
            'description': r'(?i)(?:detailed description|description of the preferred embodiment|description of embodiments)[\s\n]*(.*?)(?=\n(?:claims|what is claimed)|\Z)',
            'claims': r'(?i)(?:claims|what is claimed)[\s\n]*(.*?)(?=\Z)'
        }
        
        text_remaining = patent_text
        
        for section_name, pattern in patterns.items():
            match = re.search(pattern, text_remaining, re.DOTALL | re.IGNORECASE)
            if match:
                sections[section_name] = match.group(1).strip()
                # Remove matched content from remaining text
                text_remaining = re.sub(pattern, '', text_remaining, flags=re.DOTALL | re.IGNORECASE)
        
        # Any remaining text goes to 'other'
        sections['other'] = text_remaining.strip()
        
        return sections

# Utility functions
def chunk_patent_document(
    patent_text: str,
    document_id: str,
    strategy: str = 'tokens',
    chunk_size: int = 1000,
    overlap: int = 200
) -> List[TextChunk]:
    """
    Convenience function to chunk a patent document using specified strategy
    
    Args:
        patent_text: Full patent document text
        document_id: Unique identifier for the document
        strategy: Chunking strategy ('tokens', 'sections', 'paragraphs')
        chunk_size: Maximum tokens per chunk
        overlap: Overlap between chunks (for token strategy)
        
    Returns:
        List of TextChunk objects
    """
    chunker = PatentChunker(chunk_size=chunk_size, overlap=overlap)
    
    if strategy == 'tokens':
        return chunker.chunk_by_tokens(patent_text, document_id)
    elif strategy == 'sections':
        return chunker.chunk_by_sections(patent_text, document_id)
    elif strategy == 'paragraphs':
        return chunker.chunk_by_paragraphs(patent_text, document_id)
    else:
        raise ValueError(f"Unknown chunking strategy: {strategy}")

def optimize_chunks_for_embeddings(chunks: List[TextChunk], min_size: int = 100) -> List[TextChunk]:
    """
    Optimize chunks for embedding generation by filtering out very short chunks
    and combining adjacent small chunks
    
    Args:
        chunks: List of TextChunk objects
        min_size: Minimum number of tokens per chunk
        
    Returns:
        Optimized list of TextChunk objects
    """
    chunker = PatentChunker()
    optimized_chunks = []
    
    i = 0
    while i < len(chunks):
        current_chunk = chunks[i]
        current_tokens = chunker.count_tokens(current_chunk.content)
        
        # If chunk is too small, try to combine with next chunk
        if current_tokens < min_size and i < len(chunks) - 1:
            next_chunk = chunks[i + 1]
            combined_content = current_chunk.content + "\n\n" + next_chunk.content
            combined_tokens = chunker.count_tokens(combined_content)
            
            # If combined chunk is reasonable size, combine them
            if combined_tokens <= chunker.chunk_size:
                combined_chunk = TextChunk(
                    content=combined_content,
                    start_index=current_chunk.start_index,
                    end_index=next_chunk.end_index,
                    chunk_id=f"{current_chunk.chunk_id}_combined",
                    metadata={
                        'token_count': combined_tokens,
                        'combined_from': [current_chunk.chunk_id, next_chunk.chunk_id],
                        'chunk_type': 'optimized_combined'
                    }
                )
                optimized_chunks.append(combined_chunk)
                i += 2  # Skip next chunk since it's been combined
                continue
        
        # Keep chunk if it meets minimum size or can't be combined
        if current_tokens >= min_size:
            optimized_chunks.append(current_chunk)
        
        i += 1
    
    return optimized_chunks