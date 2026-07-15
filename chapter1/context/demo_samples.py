#!/usr/bin/env python3
"""
Demo script to showcase sample tasks with PDF functionality
"""

import os
import sys
from pathlib import Path
from main import get_sample_tasks, ensure_sample_pdfs

def main():
    """Demo the sample tasks"""
    print("\n" + "="*60)
    print("🎯 CONTEXT-AWARE AGENT - SAMPLE TASKS DEMO")
    print("="*60)
    
    # Ensure PDFs exist
    print("\n📄 Checking for sample PDFs...")
    if ensure_sample_pdfs():
        print("✅ Sample PDFs are ready!")
    else:
        print("⚠️ Could not create sample PDFs, will use online alternatives")
    
    # Get sample tasks
    tasks = get_sample_tasks()
    
    print(f"\n📋 Found {len(tasks)} sample tasks:")
    print("-"*60)
    
    for i, task in enumerate(tasks, 1):
        print(f"\n{i}. {task['name']}")
        print(f"   📝 {task['description']}")
        print(f"   📊 Complexity: {'⭐' * (i if i <= 3 else 3)}")
        
        # Show a preview of the task
        task_preview = task['task'].replace('\n', ' ')[:100] + "..."
        print(f"   💬 Preview: {task_preview}")
    
    print("\n" + "="*60)
    print("💡 USAGE TIPS:")
    print("-"*60)
    print("1. Run 'python main.py' to enter interactive mode")
    print("2. Type 'sample 3' to test PDF parsing capabilities")
    print("3. Type 'sample 5' for the most comprehensive test")
    print("4. Switch modes with 'mode no_reasoning' to see ablation effects")
    
    print("\n" + "="*60)
    print("🔬 ABLATION TESTING:")
    print("-"*60)
    print("Try running the same task in different modes:")
    print("  • full         - Everything works perfectly")
    print("  • no_history   - Agent forgets what it did")
    print("  • no_reasoning - No planning, chaotic execution")
    print("  • no_tool_calls - Can't do anything!")
    print("  • no_tool_results - Works blind, gets confused")
    
    print("\n" + "="*60)
    print("📊 PDF TASKS:")
    print("-"*60)
    
    # Check if local PDFs exist
    pdf_dir = Path("test_pdfs")
    if pdf_dir.exists():
        pdfs = list(pdf_dir.glob("*.pdf"))
        if pdfs:
            print(f"✅ Found {len(pdfs)} local PDF files:")
            for pdf in pdfs:
                print(f"   • {pdf.name}")
            print("\nTask #3 will use these local PDFs for testing.")
        else:
            print("⚠️ No PDFs found in test_pdfs/")
    else:
        print("📥 PDF directory not found. Run 'create_pdfs' command to generate samples.")
    
    print("\n" + "="*60)
    print("Ready to test! Run 'python main.py' to start.")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
