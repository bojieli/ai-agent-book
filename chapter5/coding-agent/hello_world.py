#!/usr/bin/env python3

from typing import Any

def greet(name: str) -> str:
    """Return a friendly greeting for the given name."""
    return f"Hello, {name}!"


def main() -> None:
    # Requirement 1: Print "Hello, World!"
    print("Hello, World!")

    # Requirement 3: Demonstrate the function
    print(greet("Alice"))


if __name__ == "__main__":
    main()
