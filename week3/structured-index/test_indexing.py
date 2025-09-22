"""
Test script for structured indexing with sample Intel x86 instruction documentation.
"""

import asyncio
from pathlib import Path
from loguru import logger

from config import get_raptor_config, get_graphrag_config
from raptor_indexer import RaptorIndexer
from graphrag_indexer import GraphRAGIndexer
from document_processor import DocumentProcessor


# Sample Intel x86/x64 instruction documentation text
SAMPLE_INTEL_DOC = """
Chapter 3: Basic Execution Environment

The Intel 64 and IA-32 architectures provide a comprehensive execution environment for running applications. 
This chapter describes the basic elements of this environment including registers, memory organization, and instruction formats.

3.1 General-Purpose Registers

The general-purpose registers are used for arithmetic, logic, and memory operations. In 64-bit mode, there are 16 general-purpose registers:
- RAX, RBX, RCX, RDX: Traditional registers extended to 64 bits
- RSI, RDI, RBP, RSP: Index and pointer registers
- R8-R15: Additional registers available in 64-bit mode

Each register can be accessed as:
- 64-bit (RAX, RBX, etc.)
- 32-bit (EAX, EBX, etc.) 
- 16-bit (AX, BX, etc.)
- 8-bit (AL/AH, BL/BH, etc.)

3.2 Instruction Format

Intel 64 and IA-32 instruction formats consist of:
1. Instruction prefixes (optional)
2. Primary opcode (1-3 bytes)
3. ModR/M byte (if required)
4. SIB byte (if required)
5. Displacement (if required)
6. Immediate data (if required)

MOV Instruction:
MOV - Move data between registers or between register and memory
The MOV instruction copies the source operand to the destination operand without affecting the source.

Syntax:
MOV destination, source

Examples:
MOV RAX, RBX     ; Move RBX to RAX
MOV [RDI], RSI   ; Move RSI to memory location pointed by RDI
MOV ECX, 42      ; Move immediate value 42 to ECX

ADD Instruction:
ADD - Add two operands
The ADD instruction adds the source operand to the destination operand and stores the result in the destination.

Syntax:
ADD destination, source

The instruction updates the following flags: OF, SF, ZF, AF, PF, CF

JMP Instruction:
JMP - Unconditional jump
The JMP instruction transfers program control to a different point in the code unconditionally.

Syntax:
JMP target

Chapter 4: SIMD Instructions

4.1 SSE Instructions

SSE (Streaming SIMD Extensions) provides 128-bit registers (XMM0-XMM15) for parallel operations on packed data.

MOVAPS - Move Aligned Packed Single-Precision Floating-Point Values
MOVAPS moves 128 bits of packed single-precision floating-point values from source to destination.

ADDPS - Add Packed Single-Precision Floating-Point Values
ADDPS performs parallel addition of four single-precision floating-point values.

4.2 AVX Instructions

AVX (Advanced Vector Extensions) extends SIMD capabilities with 256-bit registers (YMM0-YMM15).

VMOVAPS - Move Aligned Packed Single-Precision Floating-Point Values (AVX)
VMOVAPS moves 256 bits of packed single-precision floating-point values.

VADDPS - Add Packed Single-Precision Floating-Point Values (AVX)
VADDPS performs parallel addition of eight single-precision floating-point values.

Chapter 5: System Instructions

5.1 Control Registers

Control registers (CR0, CR2, CR3, CR4) control the operation mode and state of the processor:
- CR0: System control flags including protection enable and paging
- CR2: Page fault linear address
- CR3: Page directory base address
- CR4: Architecture extensions control

CPUID Instruction:
CPUID - CPU Identification
Returns processor identification and feature information in EAX, EBX, ECX, and EDX registers.

RDTSC Instruction:
RDTSC - Read Time-Stamp Counter
Reads the processor's time-stamp counter into EDX:EAX.
"""


async def test_indexing():
    """Test both RAPTOR and GraphRAG indexing with sample documentation."""
    
    logger.info("Starting structured indexing test...")
    
    # Test RAPTOR indexing
    logger.info("\n" + "="*60)
    logger.info("Testing RAPTOR Tree-Based Indexing")
    logger.info("="*60)
    
    raptor_config = get_raptor_config()
    raptor = RaptorIndexer(raptor_config)
    
    # Build index
    raptor.build_index(SAMPLE_INTEL_DOC)
    stats = raptor.get_tree_statistics()
    logger.info(f"RAPTOR Statistics: {stats}")
    
    # Test queries
    test_queries = [
        "What are the general-purpose registers?",
        "How does the MOV instruction work?",
        "What are SIMD instructions?",
        "Explain control registers"
    ]
    
    for query in test_queries:
        logger.info(f"\nQuery: {query}")
        results = raptor.search(query, top_k=3)
        for i, result in enumerate(results, 1):
            logger.info(f"{i}. Level {result['level']} (Score: {result['score']:.3f})")
            logger.info(f"   Summary: {result['summary'][:150]}...")
    
    # Save index
    raptor.save_index()
    
    # Test GraphRAG indexing
    logger.info("\n" + "="*60)
    logger.info("Testing GraphRAG Knowledge Graph Indexing")
    logger.info("="*60)
    
    graphrag_config = get_graphrag_config()
    graphrag = GraphRAGIndexer(graphrag_config)
    
    # Build knowledge graph
    graphrag.build_knowledge_graph(SAMPLE_INTEL_DOC)
    graphrag.detect_communities()
    graphrag.hierarchical_summarization()
    
    stats = graphrag.get_graph_statistics()
    logger.info(f"GraphRAG Statistics: {stats}")
    
    # Test queries
    for query in test_queries:
        logger.info(f"\nQuery: {query}")
        results = graphrag.search(query, top_k=3, search_type="hybrid")
        for i, result in enumerate(results, 1):
            if result['type'] == 'entity':
                logger.info(f"{i}. Entity: {result['name']} ({result['entity_type']}) - Score: {result['score']:.3f}")
                logger.info(f"   Description: {result['description'][:150]}...")
            else:
                logger.info(f"{i}. Community (Level {result['level']}) - Score: {result['score']:.3f}")
                logger.info(f"   Summary: {result['summary'][:150]}...")
    
    # Save index
    graphrag.save_index()
    
    logger.info("\n" + "="*60)
    logger.info("Test completed successfully!")
    logger.info("="*60)


if __name__ == "__main__":
    # Set up logging
    logger.add("test_indexing.log", rotation="10 MB")
    
    # Run the test
    asyncio.run(test_indexing())
