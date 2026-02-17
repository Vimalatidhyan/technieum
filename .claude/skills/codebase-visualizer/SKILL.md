---
name: codebase-visualizer
description: Generate an interactive collapsible tree visualization of the codebase.
allowed-tools: Bash(python *)
user-invocable: true
---

# Codebase Visualizer

Generate an interactive HTML tree view of this repository.

## Usage
- Run: `python .claude/skills/codebase-visualizer/scripts/visualize.py .`
- Output: `codebase-map.html` opened in your browser.

## What it shows
- Collapsible directories
- File sizes and counts
- Top file types by size (bar chart)

## Script
See [scripts/visualize.py](scripts/visualize.py).