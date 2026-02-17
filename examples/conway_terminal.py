#!/usr/bin/env python3
"""
conway_terminal.py

A Conway's Game of Life terminal runner using proper ECS architecture.
Each cell is an entity with Cell and Position components.

Controls:
 - Enter: step one generation  
 - r: start continuous run
 - s: stop continuous run
 - c: randomize
 - g: place a glider in the center
 - p: place a pulsar in the center
 - q: quit

Run with: python examples/conway_terminal.py (from repo root after `pip install -e .`)
"""

import sys
import os
import time
import random
import select
import termios
import tty

from dataclasses import dataclass
from typing import List, Tuple
from hive import Runtime
from hive.core import System, World


ALIVE = "O"
DEAD = "."

# Configuration
ROWS = 24
COLS = 80
TICK = 0.041 # seconds between frames when running continuously


# ECS Components
@dataclass
class Position:
    row: int
    col: int

@dataclass 
class Cell:
    alive: bool

@dataclass
class GridConfig:
    """Resource: Grid dimensions and parameters"""
    rows: int
    cols: int

def clear_terminal():
    sys.stdout.write("\x1b[2J\x1b[H")
    sys.stdout.flush()


def make_grid_entities(world: World, rows: int, cols: int, randomize: bool = True):
    """Create entities for each cell in the grid."""
    for r in range(rows):
        for c in range(cols):
            entity = world.create_entity()
            alive = random.random() < 0.25 if randomize else False
            world.add_component(entity, Position(r, c))
            world.add_component(entity, Cell(alive))


def get_grid_from_entities(world: World, rows: int, cols: int) -> List[List[int]]:
    """Convert entities back to grid for rendering."""
    grid = [[0 for _ in range(cols)] for _ in range(rows)]
    for entity, pos, cell in world.store.query(Position, Cell):
        if 0 <= pos.row < rows and 0 <= pos.col < cols:
            grid[pos.row][pos.col] = 1 if cell.alive else 0
    return grid


def count_neighbors(world: World, row: int, col: int, rows: int, cols: int) -> int:
    """Count alive neighbors for a cell using ECS query."""
    count = 0
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            nr = (row + dr) % rows
            nc = (col + dc) % cols
            # Find entity at this position
            for entity, pos, cell in world.store.query(Position, Cell):
                if pos.row == nr and pos.col == nc and cell.alive:
                    count += 1
                    break
    return count


class LifeSystem(System):
    """System that calculates next generation using efficient neighbor counting."""

    def update(self, world: World, dispatcher):
        config = world.resources.get(GridConfig)
        rows, cols = config.rows, config.cols
        
        # Build a lookup table: (row, col) -> (entity, cell)
        # This is O(n) instead of O(n²) for neighbor queries
        grid_map = {}
        for entity, pos, cell in world.store.query(Position, Cell):
            grid_map[(pos.row, pos.col)] = (entity, cell)
        
        # Calculate next state for all cells
        updates = []  # (entity, new_alive_state)
        
        for (row, col), (entity, cell) in grid_map.items():
            # Count neighbors using the lookup table
            neighbors = 0
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    nr = (row + dr) % rows
                    nc = (col + dc) % cols
                    neighbor_key = (nr, nc)
                    if neighbor_key in grid_map:
                        _, neighbor_cell = grid_map[neighbor_key]
                        if neighbor_cell.alive:
                            neighbors += 1
            
            if cell.alive:
                # Alive: stays alive with 2 or 3 neighbors
                new_state = neighbors in (2, 3)
            else:
                # Dead: becomes alive with exactly 3 neighbors
                new_state = neighbors == 3
            
            if new_state != cell.alive:
                updates.append((entity, new_state))
        
        # Apply updates
        for entity, new_alive in updates:
            # Find and update the cell component
            for (row, col), (e, cell) in grid_map.items():
                if e == entity:
                    cell.alive = new_alive
                    break


class RenderSystem(System):
    """System that renders the grid to terminal."""

    def update(self, world: World, dispatcher):
        config = world.resources.get(GridConfig)
        rows, cols = config.rows, config.cols
        
        grid = get_grid_from_entities(world, rows, cols)
        
        out_lines = []
        for row in grid:
            out_lines.append("".join(ALIVE if c else DEAD for c in row))
        
        buf = "\n".join(out_lines)
        world.resources.register(RenderBuffer(buf))


@dataclass
class RenderBuffer:
    """Resource: Rendered output buffer"""
    content: str


def center_pattern(world: World, pattern: List[Tuple[int, int]], rows: int, cols: int):
    """Place a pattern at the center of the grid."""
    r0 = rows // 2
    c0 = cols // 2
    
    # Clear all cells first
    for entity, pos, cell in world.store.query(Position, Cell):
        cell.alive = False
    
    # Set pattern cells
    for dr, dc in pattern:
        rr = (r0 + dr) % rows
        cc = (c0 + dc) % cols
        for entity, pos, cell in world.store.query(Position, Cell):
            if pos.row == rr and pos.col == cc:
                cell.alive = True
                break


GLIDER = [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)]
PULSAR = [
    (-4, -2), (-4, -1), (-4, 0), (-4, 1), (-4, 2),
    (-2, -4), (-1, -4), (0, -4), (1, -4), (2, -4),
    (4, -2), (4, -1), (4, 0), (4, 1), (4, 2),
    (-2, 4), (-1, 4), (0, 4), (1, 4), (2, 4),
]

def get_char_nonblocking():
    """Get a single character without blocking, or return None."""
    # Check if input is available
    if select.select([sys.stdin], [], [], 0)[0]:
        return sys.stdin.read(1)
    return None


def render_current_state(runtime, world: World):
    """Step and render current state."""
    runtime.step()
    try:
        buf = runtime.world.resources.get(RenderBuffer)
        clear_terminal()
        sys.stdout.write(buf.content + "\n")
        sys.stdout.flush()
    except KeyError:
        pass


def run_terminal(rows=ROWS, cols=COLS):
    runtime = Runtime()
    world = runtime.world
    
    # Register grid config as resource
    runtime.world.resources.register(GridConfig(rows, cols))
    
    # Create entities for all cells
    make_grid_entities(world, rows, cols, randomize=True)
    
    # Register systems
    world.register(LifeSystem(), priority=0)
    world.register(RenderSystem(), priority=1)

    # Initial render
    clear_terminal()
    grid = get_grid_from_entities(world, rows, cols)
    for row in grid:
        print("".join(ALIVE if c else DEAD for c in row))
    
    print("\nControls: Enter=step, r=run, s=stop, c=randomize, g=glider, p=pulsar, q=quit")

    # Check if we're running interactively
    is_tty = sys.stdin.isatty()
    
    if is_tty:
        # Interactive mode with non-blocking input
        old_settings = termios.tcgetattr(sys.stdin)
        try:
            tty.setcbreak(sys.stdin.fileno())
            _run_interactive_loop(runtime, world, rows, cols)
        finally:
            # Restore terminal settings
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            sys.stdout.write("\nExiting.\n")
    else:
        # Non-interactive mode (piped input) - just do a few steps
        sys.stdout.write("\nNon-interactive mode - running 3 steps...\n")
        sys.stdout.flush()
        for i in range(3):
            time.sleep(0.1)
            runtime.step()
            sys.stdout.write(f"Step {i+1}/3\n")
            sys.stdout.flush()


def _run_interactive_loop(runtime, world: World, rows, cols):
    """Main interactive loop with non-blocking input."""
    running = False
    last_step = 0
    
    while True:
        # Check for input (non-blocking)
        char = get_char_nonblocking()
        
        if char:
            if char == '\n' or char == '\r':  # Enter key
                render_current_state(runtime, world)
                running = False
                
            elif char == 'r':
                running = True
                last_step = time.time()
                
            elif char == 's':
                running = False
                
            elif char == 'c':
                # Destroy all entities and recreate
                for entity in list(world.store.query_entities(Position, Cell)):
                    world.destroy_entity(entity)
                make_grid_entities(world, rows, cols, randomize=True)
                render_current_state(runtime, world)
                running = False
                
            elif char == 'g':
                center_pattern(world, GLIDER, rows, cols)
                render_current_state(runtime, world)
                running = False
                
            elif char == 'p':
                center_pattern(world, PULSAR, rows, cols)
                render_current_state(runtime, world)
                running = False
                
            elif char == 'q':
                break
        
        # Auto-step if running
        if running:
            now = time.time()
            if now - last_step >= TICK:
                render_current_state(runtime, world)
                last_step = now
            else:
                time.sleep(now - last_step)
        else:
            # Small sleep to prevent CPU spinning when idle
            time.sleep(0.01)


if __name__ == "__main__":
    try:
        run_terminal()
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        traceback.print_exc()
        raise
