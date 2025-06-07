import re
from collections import defaultdict, deque
import operator

class ReactiveVariable:
    """Represents a reactive variable with expression and dependencies."""
    def __init__(self, name, expression):
        self.name = name
        self.expression = expression
        self.dependencies = set()
        self.value = None

    def extract_dependencies(self):
        # Match all variable names (e.g., a, b)
        tokens = re.findall(r'\b[a-zA-Z_]\w*\b', self.expression)
        self.dependencies = set(filter(lambda x: not x.isdigit() and x != 'input', tokens))

class ReactiveSystem:
    def __init__(self):
        self.variables = {}
        self.reverse_dependencies = defaultdict(set)
        self.topo_order = []

    def add_variable(self, line):
        _, name, _, expr = line.split(' ', 3)
        var = ReactiveVariable(name, expr)
        var.extract_dependencies()
        self.variables[name] = var
        for dep in var.dependencies:
            self.reverse_dependencies[dep].add(name)

    def build_topo_order(self):
        in_degree = {var: 0 for var in self.variables}
        for var in self.variables.values():
            for dep in var.dependencies:
                in_degree[var.name] += 1

        queue = deque([v for v in self.variables if in_degree[v] == 0])
        self.topo_order = []

        while queue:
            current = queue.popleft()
            self.topo_order.append(current)
            for dependent in self.reverse_dependencies.get(current, []):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

    def evaluate_expression(self, expr, values):
        # Custom safe parser and evaluator (supports +, -, *, //)
        tokens = expr.split()
        stack = []

        ops = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '//': operator.floordiv,
        }

        # Convert infix to postfix (Shunting Yard algorithm can be used for complex cases)
        postfix = []
        for token in tokens:
            if token in ops:
                postfix.append(token)
            else:
                postfix.append(values.get(token, token))

        # Evaluate postfix expression
        result_stack = []
        for token in postfix:
            if str(token).isdigit():
                result_stack.append(int(token))
            elif token in values:
                result_stack.append(values[token])
            elif token in ops:
                b = result_stack.pop()
                a = result_stack.pop()
                result_stack.append(ops[token](a, b))
        return result_stack[0] if result_stack else None

    def evaluate_all(self):
        values = {}
        for var_name in self.topo_order:
            var = self.variables[var_name]
            if var.expression == 'input':
                values[var_name] = var.value  # Set manually via event
            else:
                values[var_name] = self.evaluate_expression(var.expression, values)
            var.value = values[var_name]

    def handle_event(self, var_name, new_value):
        self.variables[var_name].value = int(new_value)

        affected = set()
        queue = deque([var_name])
        while queue:
            current = queue.popleft()
            for dep in self.reverse_dependencies.get(current, []):
                if dep not in affected:
                    affected.add(dep)
                    queue.append(dep)

        self.evaluate_all()

        # Print all affected variables in topo order
        print(f"{var_name} = {new_value}")
        for var in self.topo_order:
            if var == var_name or var in affected:
                print(f"{var} = {self.variables[var].value}")

    def process(self, lines):
        for line in lines:
            if line.startswith('var'):
                self.add_variable(line)

        self.build_topo_order()
        self.evaluate_all()

        for line in lines:
            if line.startswith('event'):
                _, var, _, val = line.split()
                self.handle_event(var, val)
