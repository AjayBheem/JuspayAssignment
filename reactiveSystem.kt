import java.util.*

class ReactiveVariable(val name: String, val expression: String) {
    val dependencies = mutableSetOf<String>()
    var value: Int? = null

    init {
        val regex = Regex("""\b[a-zA-Z_]\w*\b""")
        val tokens = regex.findAll(expression).map { it.value }.filter { it != "input" }.toSet()
        dependencies.addAll(tokens)
    }
}

class ReactiveSystem {
    val variables = mutableMapOf<String, ReactiveVariable>()
    val reverseDeps = mutableMapOf<String, MutableSet<String>>()
    val topoOrder = mutableListOf<String>()

    fun addVariable(line: String) {
        val parts = line.split(" ", limit = 4)
        val name = parts[1]
        val expr = parts[3]
        val variable = ReactiveVariable(name, expr)
        variables[name] = variable

        for (dep in variable.dependencies) {
            reverseDeps.getOrPut(dep) { mutableSetOf() }.add(name)
        }
    }

    fun buildTopoOrder() {
        val inDegree = mutableMapOf<String, Int>()
        for (v in variables.keys) inDegree[v] = 0
        for (v in variables.values) {
            for (dep in v.dependencies) {
                inDegree[v.name] = inDegree.getOrDefault(v.name, 0) + 1
            }
        }
        val queue: Queue<String> = LinkedList()
        for ((k, deg) in inDegree) if (deg == 0) queue.add(k)

        while (queue.isNotEmpty()) {
            val current = queue.remove()
            topoOrder.add(current)
            for (dep in reverseDeps[current] ?: emptySet()) {
                inDegree[dep] = inDegree.getOrDefault(dep, 0) - 1
                if (inDegree[dep] == 0) queue.add(dep)
            }
        }
    }

    fun evaluateAll() {
        val values = mutableMapOf<String, Int>()
        for (v in topoOrder) {
            val variable = variables[v]!!
            if (variable.expression == "input") {
                values[v] = variable.value ?: 0
            } else {
                values[v] = evaluateExpression(variable.expression, values)
            }
            variable.value = values[v]
        }
    }

    fun evaluateExpression(expr: String, values: Map<String, Int>): Int {
        val tokens = expr.split(" ")
        var result = 0
        var op = "+"
        for (token in tokens) {
            when (token) {
                "+" -> op = "+"
                "*" -> op = "*"
                else -> {
                    val valToken = values[token] ?: token.toIntOrNull() ?: 0
                    result = when (op) {
                        "+" -> result + valToken
                        "*" -> result * valToken
                        else -> result
                    }
                }
            }
        }
        return result
    }

    fun handleEvent(varName: String, newValue: Int) {
        variables[varName]?.value = newValue

        val affected = mutableSetOf<String>()
        val queue: Queue<String> = LinkedList()
        queue.add(varName)

        while (queue.isNotEmpty()) {
            val current = queue.remove()
            for (dep in reverseDeps[current] ?: emptySet()) {
                if (affected.add(dep)) queue.add(dep)
            }
        }
        evaluateAll()
        println("$varName = $newValue")
        for (v in topoOrder) {
            if (v == varName || affected.contains(v)) {
                println("$v = ${variables[v]?.value}")
            }
        }
    }

    fun process(lines: List<String>) {
        lines.forEach {
            if (it.startsWith("var ")) addVariable(it)
        }
        buildTopoOrder()
        evaluateAll()
        lines.forEach {
            if (it.startsWith("event ")) {
                val parts = it.split(" ")
                handleEvent(parts[1], parts[3].toInt())
            }
        }
    }
}

fun main() {
    val input = listOf(
        "var a = input",
        "var b = a + 2",
        "var c = b * 3",
        "event a = 4",
        "event a = 6"
    )
    val system = ReactiveSystem()
    system.process(input)
}
