# Juspay SDE Assignment - Reactive Programming Simulator

## Problem Statement
Implement a reactive programming simulator where variables depend on others. On updating one variable, all dependent variables should be recalculated and printed.

## Features
- Parses variable declarations and event updates
- Tracks dependencies using a graph
- Topological sorting to evaluate variables in the right order
- Custom expression evaluation without using `eval()`
- Functional and modular Python code

## How to Run
1. Clone the repo
2. Run the Python script `reactive_simulator.py`
3. Provide input lines in the code or modify to read from file/CLI

```bash
python reactive_simulator.py
