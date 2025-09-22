"""
Script to download sample technical documentation for testing.
Since the full Intel manual is very large, this creates a sample document.
"""

import requests
from pathlib import Path
import json


def create_sample_intel_doc():
    """Create a sample Intel architecture documentation for testing."""
    
    sample_doc = """
Intel® 64 and IA-32 Architectures Software Developer's Manual
Volume 1: Basic Architecture

CHAPTER 3: BASIC EXECUTION ENVIRONMENT

3.1 MODES OF OPERATION
The IA-32 architecture supports three basic operating modes: protected mode, real-address mode, and system management mode. The operating mode determines which instructions and architectural features are accessible.

Protected mode — This mode is the native state of the processor. Among the capabilities of protected mode is the ability to directly execute "real-address mode" 8086 software in a protected, multi-tasking environment. This feature is called virtual-8086 mode.

Real-address mode — This mode implements the programming environment of the Intel 8086 processor with extensions. The processor is placed in real-address mode following power-up or a reset.

System management mode (SMM) — This mode provides an operating system or executive with a transparent mechanism for implementing platform-specific functions such as power management and system security.

3.2 OVERVIEW OF THE BASIC EXECUTION ENVIRONMENT

3.2.1 64-Bit Mode Execution Environment
When in 64-bit mode, the following architectural features become available:
• 64-bit linear addressing
• Physical address extensions to 52 bits
• 16 general-purpose registers (GPRs) in 64-bit mode
• 64-bit-wide GPRs
• 64-bit instruction pointer (RIP)
• New operating mode (64-bit mode)
• Uniform byte-register addressing
• Additional SSE registers
• Fast interrupt-prioritization mechanism

3.3 MEMORY ORGANIZATION

3.3.1 IA-32 Memory Models
When employing the processor's memory management facilities, programs do not directly address physical memory. Instead, they access memory using one of three memory models: flat, segmented, or real-address mode.

Flat memory model — Memory appears to a program as a single, continuous address space. This space is called a linear address space. Code, data, and stacks are all contained in this address space. Linear address space is byte addressable.

Segmented memory model — Memory appears to a program as a group of independent address spaces called segments. Code, data, and stacks are typically contained in separate segments.

Real-address mode memory model — This is the memory model for the Intel 8086 processor. It supports a nominally 64-KByte register-based memory model.

3.4 GENERAL-PURPOSE REGISTERS

The 64-bit extensions expand the general-purpose registers to 64 bits and add 8 new registers (R8-R15). All 16 general-purpose registers can be accessed at the byte, word, dword, and qword level.

3.4.1 General-Purpose Registers in 64-Bit Mode
In 64-bit mode, there are 16 general-purpose registers and the default operand size is 32 bits. However, general-purpose registers can be accessed as 64-bit, 32-bit, 16-bit, or 8-bit values.

Register set includes:
• RAX, RBX, RCX, RDX - Extended versions of EAX, EBX, ECX, EDX
• RBP, RSI, RDI, RSP - Extended versions of EBP, ESI, EDI, ESP
• R8-R15 - New registers introduced with 64-bit extensions

3.4.2 Register Operand-Size Encoding
In 64-bit mode, the default operand size for most instructions is 32 bits. A REX prefix specifies a 64-bit operand size. Operand sizes of 8 bits and 16 bits are also available.

CHAPTER 4: INSTRUCTION SET REFERENCE

4.1 INSTRUCTION FORMAT
All Intel 64 and IA-32 instruction encodings are subsets of the general instruction format shown below. Instructions consist of optional instruction prefixes, primary opcode bytes, an addressing-form specifier (if required), a displacement (if required), and an immediate data field (if required).

4.2 DATA MOVEMENT INSTRUCTIONS

MOV—Move
Copies the second operand (source operand) to the first operand (destination operand). The source operand can be an immediate value, general-purpose register, segment register, or memory location.

Operation:
DEST ← SRC;

Flags Affected:
None

Protected Mode Exceptions:
#GP(0) If the destination operand is in a non-writable segment
#GP(0) If a memory operand effective address is outside the CS, DS, ES, FS, or GS segment limit
#SS(0) If a memory operand effective address is outside the SS segment limit
#PF(fault-code) If a page fault occurs
#AC(0) If alignment checking is enabled

MOVSX/MOVSXD—Move with Sign-Extension
Copies the contents of the source operand to the destination operand and sign extends the value. The size of the converted value depends on the operand-size attribute.

MOVZX—Move with Zero-Extend
Copies the contents of the source operand to the destination operand and zero extends the value.

XCHG—Exchange Register/Memory with Register
Exchanges the contents of the destination (first) and source (second) operands. The operands can be two general-purpose registers or a register and a memory location.

4.3 ARITHMETIC INSTRUCTIONS

ADD—Add
Adds the destination operand (first operand) and the source operand (second operand) and then stores the result in the destination operand.

Operation:
DEST ← DEST + SRC;

Flags Affected:
The OF, SF, ZF, AF, CF, and PF flags are set according to the result.

SUB—Subtract
Subtracts the second operand (source operand) from the first operand (destination operand) and stores the result in the destination operand.

MUL—Unsigned Multiply
Performs an unsigned multiplication of the first operand (destination operand) and the second operand (source operand) and stores the result in the destination operand.

IMUL—Signed Multiply
Performs a signed multiplication and stores the result in the destination.

DIV—Unsigned Divide
Divides unsigned the value in the AX, DX:AX, EDX:EAX, or RDX:RAX registers by the source operand and stores the result in the AX (AH:AL), DX:AX, EDX:EAX, or RDX:RAX registers.

4.4 LOGICAL INSTRUCTIONS

AND—Logical AND
Performs a bitwise AND operation on the destination operand and the source operand and stores the result in the destination operand location.

OR—Logical Inclusive OR
Performs a bitwise inclusive OR operation between the destination operand and the source operand and stores the result in the destination operand location.

XOR—Logical Exclusive OR
Performs a bitwise exclusive OR operation on the destination operand and the source operand and stores the result in the destination operand.

NOT—One's Complement Negation
Performs a bitwise NOT operation on the destination operand and stores the result in the destination operand location.

4.5 CONTROL TRANSFER INSTRUCTIONS

JMP—Jump
Transfers program control to a different point in the code segment. The destination operand specifies the address of the target instruction.

Jcc—Jump if Condition Is Met
Checks the state of one or more status flags in the EFLAGS register and, if the flags are in the specified state (condition), performs a jump to the target instruction specified by the destination operand.

CALL—Call Procedure
Saves procedure linking information on the stack and branches to the called procedure specified using the target operand.

RET—Return from Procedure
Transfers program control to a return address located on the top of the stack.

4.6 STRING INSTRUCTIONS

MOVS/MOVSB/MOVSW/MOVSD/MOVSQ—Move String
Moves the byte, word, doubleword, or quadword specified with the second operand to the location specified with the first operand.

CMPS/CMPSB/CMPSW/CMPSD/CMPSQ—Compare String Operands
Compares the byte, word, doubleword, or quadword specified with the first source operand with the second source operand and sets the status flags in the EFLAGS register according to the results.

CHAPTER 5: SIMD INSTRUCTIONS

5.1 SSE INSTRUCTIONS

SSE instructions operate on packed single-precision floating-point values contained in XMM registers or memory.

MOVAPS—Move Aligned Packed Single-Precision Floating-Point Values
Moves 128 bits of packed single-precision floating-point values from the source operand to the destination operand.

MOVUPS—Move Unaligned Packed Single-Precision Floating-Point Values
Moves 128 bits of packed single-precision floating-point values from the source operand to the destination operand.

ADDPS—Add Packed Single-Precision Floating-Point Values
Performs addition of the packed single-precision floating-point values from the source operand and the destination operand, and stores the packed single-precision floating-point results in the destination operand.

SUBPS—Subtract Packed Single-Precision Floating-Point Values
Performs subtraction of the packed single-precision floating-point values in the source operand from the packed single-precision floating-point values in the destination operand.

MULPS—Multiply Packed Single-Precision Floating-Point Values
Performs multiplication of the packed single-precision floating-point values from the source operand and the destination operand.

5.2 AVX INSTRUCTIONS

AVX instructions extend SSE functionality with 256-bit YMM registers.

VMOVAPS—Move Aligned Packed Single-Precision Floating-Point Values
Moves 256 bits of packed single-precision floating-point values from the source operand to the destination operand.

VADDPS—Add Packed Single-Precision Floating-Point Values
Performs SIMD addition of the packed single-precision floating-point values from the first source operand and second source operand, and stores the packed single-precision floating-point results in the destination operand.

CHAPTER 6: SYSTEM PROGRAMMING

6.1 SYSTEM REGISTERS

Control Registers
Control registers (CR0, CR2, CR3, and CR4) control the operation of the processor and the characteristics of the currently executing task.

CR0—Contains system control flags that control operating mode and states of the processor
CR1—Reserved
CR2—Contains the page-fault linear address
CR3—Contains the physical address of the base of the paging-structure hierarchy
CR4—Contains a group of flags that enable several architectural extensions

6.2 SYSTEM INSTRUCTIONS

CPUID—CPU Identification
Returns processor identification and feature information in the EAX, EBX, ECX, and EDX registers. The instruction's output depends on the contents of the EAX register upon execution.

RDTSC—Read Time-Stamp Counter
Reads the current value of the processor's time-stamp counter (a 64-bit MSR) into the EDX:EAX registers.

RDMSR—Read from Model Specific Register
Reads the contents of a 64-bit model specific register (MSR) specified in the ECX register into registers EDX:EAX.

WRMSR—Write to Model Specific Register
Writes the contents of registers EDX:EAX into the 64-bit model specific register (MSR) specified in the ECX register.
"""
    
    # Save as a text file
    output_path = Path("sample_intel_manual.txt")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(sample_doc)
    
    print(f"Created sample Intel documentation: {output_path}")
    print(f"File size: {len(sample_doc)} characters")
    return str(output_path)


def create_sample_queries():
    """Create sample queries for testing."""
    
    queries = [
        # Basic instruction queries
        "What is the MOV instruction and how does it work?",
        "Explain the difference between MOVSX and MOVZX",
        "What are the arithmetic instructions in x86?",
        
        # Register queries
        "What are the general-purpose registers in 64-bit mode?",
        "How many general-purpose registers are available in x86-64?",
        "What is the purpose of control registers CR0-CR4?",
        
        # Memory model queries
        "What are the different memory models in IA-32 architecture?",
        "Explain the flat memory model",
        "What is the difference between segmented and flat memory models?",
        
        # SIMD queries
        "What are SSE instructions?",
        "What is the difference between SSE and AVX?",
        "How do MOVAPS and MOVUPS differ?",
        
        # System programming queries
        "What does the CPUID instruction do?",
        "How do I read the time-stamp counter?",
        "What are model specific registers (MSRs)?",
        
        # Complex queries
        "How do string instructions work in x86?",
        "What are the different operating modes in IA-32?",
        "Explain the instruction format in Intel 64 architecture",
        
        # Relationship queries (good for GraphRAG)
        "What is the relationship between MOV and XCHG instructions?",
        "How are ADD and SUB instructions related?",
        "Which instructions affect the FLAGS register?",
    ]
    
    # Save queries
    queries_path = Path("sample_queries.json")
    with open(queries_path, 'w', encoding='utf-8') as f:
        json.dump(queries, f, indent=2)
    
    print(f"Created {len(queries)} sample queries: {queries_path}")
    return queries


if __name__ == "__main__":
    print("Creating sample Intel architecture documentation...")
    doc_path = create_sample_intel_doc()
    
    print("\nCreating sample queries...")
    queries = create_sample_queries()
    
    print("\n" + "="*60)
    print("Sample data created successfully!")
    print("="*60)
    
    print("\nTo test the system:")
    print("1. Build indexes:")
    print(f"   python main.py build {doc_path} --type both")
    print("\n2. Start API server:")
    print("   python main.py serve")
    print("\n3. Test with queries:")
    print("   python main.py query \"What is the MOV instruction?\"")
    print("\n4. Run comprehensive test:")
    print("   python test_indexing.py")
