#!/usr/bin/env python3
"""Demonstration of UI improvements for test case selection"""

import os
import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Mock environment for demo
os.environ["KIMI_API_KEY"] = "demo_key"

console = Console()


def demo_single_test_selection():
    """Demonstrate the improved single test case selection"""
    console.print("\n[bold cyan]Improved Single Test Case Selection[/bold cyan]")
    console.print("="*60)
    
    # Simulated test cases
    test_cases = {
        "layer1_01_bank_account": "Bank Account Setup - Personal Details Retrieval",
        "layer1_02_insurance_claim": "Insurance Claim - Policy and Representative Information",
        "layer1_03_medical_appointment": "Medical Appointment - Doctor and Schedule Details",
        "layer2_01_multiple_vehicles": "Multiple Vehicles - Service Scheduling Conflict",
        "layer2_02_multiple_properties": "Multiple Properties - Maintenance Priorities",
        "layer3_01_travel_coordination": "Travel Coordination - Multi-Factor Planning"
    }
    
    console.print("\n[bold]Available Test Cases:[/bold]")
    
    # Group by category
    categories = {
        "layer1": [],
        "layer2": [],
        "layer3": []
    }
    
    for test_id, title in test_cases.items():
        cat = test_id.split("_")[0]
        categories[cat].append((test_id, title))
    
    # Display with numbers
    test_ids_list = []
    for cat in sorted(categories.keys()):
        console.print(f"\n[cyan]{cat.upper()}:[/cyan]")
        for test_id, title in categories[cat]:
            test_ids_list.append(test_id)
            idx = len(test_ids_list)
            console.print(f"  [{idx}] {test_id}: {title[:60]}...")
    
    console.print("\n[dim]Enter test ID directly or number from the list above[/dim]")
    console.print("[yellow]Example inputs: '3' or 'layer1_03_medical_appointment'[/yellow]")


def demo_view_test_cases_table():
    """Demonstrate the improved test cases table with index numbers"""
    console.print("\n[bold cyan]Improved Test Cases Table View[/bold cyan]")
    console.print("="*60)
    
    # Create table with index numbers
    table = Table(title="Loaded Test Cases")
    table.add_column("#", style="dim", width=4)
    table.add_column("ID", style="cyan")
    table.add_column("Category", style="magenta")
    table.add_column("Title", style="green")
    table.add_column("Conversations", justify="right")
    
    # Sample data
    test_data = [
        ("layer1_01_bank_account", "layer1", "Bank Account Setup - Personal Details Retrieval", "1"),
        ("layer1_02_insurance_claim", "layer1", "Insurance Claim - Policy and Representative Info", "1"),
        ("layer2_01_multiple_vehicles", "layer2", "Multiple Vehicles - Service Scheduling Conflict", "2"),
        ("layer3_01_travel_coordination", "layer3", "Travel Coordination - Multi-Factor Planning", "3")
    ]
    
    for idx, (test_id, category, title, convs) in enumerate(test_data, 1):
        table.add_row(
            str(idx),
            test_id,
            category,
            title[:50] + "..." if len(title) > 50 else title,
            convs
        )
    
    console.print(table)
    console.print("\n[yellow]Users can now select by entering either:[/yellow]")
    console.print("  • The index number (e.g., '2')")
    console.print("  • The full test ID (e.g., 'layer1_02_insurance_claim')")


def demo_category_evaluation():
    """Demonstrate the improved category evaluation selection"""
    console.print("\n[bold cyan]Improved Category Evaluation[/bold cyan]")
    console.print("="*60)
    
    console.print("\n[bold]Available Categories:[/bold]")
    console.print("  layer1: 20 test cases")
    console.print("  layer2: 20 test cases")
    console.print("  layer3: 20 test cases")
    
    console.print("\n[dim]After selecting a category, you'll see:[/dim]")
    
    console.print(f"\n[cyan]Test cases in layer1:[/cyan]")
    sample_cases = [
        ("layer1_01_bank_account", "Bank Account Setup - Personal Details Retrieval"),
        ("layer1_02_insurance_claim", "Insurance Claim - Policy and Representative Info"),
        ("layer1_03_medical_appointment", "Medical Appointment - Doctor and Schedule Details")
    ]
    
    for test_id, title in sample_cases:
        console.print(f"  • {test_id}: {title[:60]}...")
    console.print("  [dim]... (17 more test cases)[/dim]")
    
    console.print(f"\n[cyan]Total: 20 test cases[/cyan]")
    console.print("[yellow]User can review the list before confirming evaluation[/yellow]")


def main():
    """Run all UI improvement demonstrations"""
    console.print(Panel.fit(
        "[bold]UI Improvements Demo - Test Case Selection[/bold]\n"
        "Showing how the improved interface helps users select test cases",
        border_style="cyan"
    ))
    
    # Demo 1: Single test selection
    demo_single_test_selection()
    
    # Demo 2: Table view with indices
    console.print("\n" + "="*80 + "\n")
    demo_view_test_cases_table()
    
    # Demo 3: Category evaluation
    console.print("\n" + "="*80 + "\n")
    demo_category_evaluation()
    
    console.print("\n" + "="*80)
    console.print("[bold green]Summary of Improvements:[/bold green]")
    console.print("✓ Test cases are displayed with index numbers for easy selection")
    console.print("✓ Users can select by number OR by test ID")
    console.print("✓ Categories show test case counts before evaluation")
    console.print("✓ Test case lists are shown before batch evaluation")
    console.print("✓ No need to memorize or guess test IDs")
    console.print("="*80 + "\n")


if __name__ == "__main__":
    main()
