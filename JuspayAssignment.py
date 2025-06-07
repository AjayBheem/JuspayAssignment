import re
from collections import defaultdict, deque

class ReactiveSimulator:
    def __init__(self):
        self.expressions = {}      # var -> expression
        self.values = {}           # var -> current value
        self.dependencies = {}     # var -> set of dependent vars
        self.reverse_deps = defaultdict(set)  # var -> who depends on var
        self.topo_order = []       # variables in topological order

    def parse_var(self, line):
        # e.g., var b = a + 2
        _, var_name, _, expr = line.split(' ', 3)
        self.expressions[var_name] = expr
        tokens = re.findall(r'\b[a-zA-Z_]\w*\b', expr)
        deps = set(filter(lambda x: x != 'input', tokens))
        self.dependencies[var_name] = deps
        for dep in deps:
            self.reverse_deps[dep].add(var_name)

    def topological_sort(self):
        in_degree = defaultdict(int)
        for var in self.expressions:
            for dep in self.dependencies.get(var, []):
                in_degree[var] += 1

        queue = deque([var for var in self.expressions if in_degree[var] == 0])
        self.topo_order = []

        while queue:
            var = queue.popleft()
            self.topo_order.append(var)
            for dep in self.reverse_deps.get(var, []):
                in_degree[dep] -= 1
                if in_degree[dep] == 0:
                    queue.append(dep)

    def evaluate_expr(self, expr):
        try:
            return eval(expr, {}, self.values)
        except:
            return None

    def evaluate_all(self):
        for var in self.topo_order:
            if self.expressions[var] == 'input':
                continue
            expr = self.expressions[var]
            self.values[var] = self.evaluate_expr(expr)

    def process_event(self, var, value):
        self.values[var] = int(value)

        # BFS to find all affected variables
        queue = deque([var])
        affected = set()

        while queue:
            current = queue.popleft()
            for dep in self.reverse_deps.get(current, []):
                if dep not in affected:
                    affected.add(dep)
                    queue.append(dep)

        affected = sorted(affected, key=lambda x: self.topo_order.index(x))
        for var in affected:
            expr = self.expressions[var]
            self.values[var] = self.evaluate_expr(expr)

        # Print all updated values
        print(f"{var} = {value}")
        for v in affected:
            print(f"{v} = {self.values[v]}")

    def process(self, lines):
        for line in lines:
            line = line.strip()
            if line.startswith('var'):
                self.parse_var(line)

        self.topological_sort()
        self.evaluate_all()

        for line in lines:
            line = line.strip()
            if line.startswith('event'):
                _, var, _, val = line.split()
                self.process_event(var, val)

# Example usage:
input_lines = [
    "var a = input",
    "var b = a + 2",
    "var c = b * 3",
    "event a = 4",
    "event a = 6"
]

sim = ReactiveSimulator()
sim.process(input_lines)
