"""
Maze Generator Package - A reusable maze generation library

This module provides multiple maze generation algorithms
and solving capabilities.

Quick Start:
    >>> from mazegen import MazeGenDFS
    >>> from config_parser import MazeConfig
    >>> 
    >>> config = MazeConfig(width=21, height=21, seed=42)
    >>> generator = MazeGenDFS(config)
    >>> generator.generate()
    >>> solution = generator.solution

Classes:
    - MazeGen: Abstract base class for maze generators
    - MazeGenDFS: Generates mazes using Depth-First Search algorithm
    - MazeGenPrim: Generates mazes using Prim's algorithm
    - MazeGenError: Exception for maze generation errors

Accessing Generated Data:
    - generator.solution: List of (x, y) coordinates from entry to exit
    - generator._get_final_grid(): 2D list of cell wall configurations
    - generator.history: List of passages carved during generation
    - generator.pattern_42: Set of coordinates containing the 42 pattern
"""

from .generator import MazeGen, MazeGenError, MazeGenDFS, MazeGenPrim
from .solver import solve

__version__ = "1.0.0"
__all__ = ['MazeGen', 'MazeGenError', 'MazeGenDFS', 'MazeGenPrim', 'solve']
