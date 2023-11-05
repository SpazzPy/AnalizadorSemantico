import ast  # Importa el modulo 'ast' que se utiliza para analizar el codigo fuente de Python.

# Define una clase VarSymbol para representar simbolos de variables con nombre y tipo.
class VarSymbol:
    def __init__(self, name, type):
        self.name = name  # El nombre de la variable.
        self.type = type  # El tipo de la variable.

# Define la clase SemanticAnalyzer que hereda de ast.NodeVisitor para realizar el analisis semantico.
class SemanticAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.symbol_table = [{}]  # Inicializa una tabla de simbolos (inicialmente vacia).

    # Define el metodo visit_Name para visitar nodos de nombres (variables).
    def visit_Name(self, node):
        variable_name = node.id  # Obtiene el nombre de la variable desde el nodo.
        # Comprueba si el nombre de la variable existe en alguno de los ambitos de la tabla de simbolos.
        if not any(variable_name in scope for scope in self.symbol_table):
            raise ValueError(f"Variable no definida: '{variable_name}'")

    # Define el metodo visit_FunctionDef para visitar nodos de definiciones de funciones.
    def visit_FunctionDef(self, node):
        self.symbol_table[-1][node.name] = VarSymbol(node.name, 'function')  # Agrega la funcion a la tabla de simbolos.
        # Agrega los argumentos de la funcion a la tabla de simbolos con el tipo 'variable'.
        for arg in node.args.args:
            self.symbol_table[-1][arg.arg] = VarSymbol(arg.arg, 'variable')
        self.generic_visit(node)  # Continua visitando el resto del nodo.

    # Define el metodo visit_ClassDef para visitar nodos de definiciones de clases.
    def visit_ClassDef(self, node):
        self.symbol_table[-1][node.name] = VarSymbol(node.name, 'class')  # Agrega la clase a la tabla de simbolos.
        self.generic_visit(node)  # Continua visitando el resto del nodo.

    # Define el metodo visit_Assign para visitar nodos de asignaciones.
    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                variable_name = target.id  # Obtiene el nombre de la variable de la asignacion.
                value_type = self.get_value_type(node.value)  # Obtiene el tipo del valor asignado.
                # Agrega la variable a la tabla de simbolos con su tipo.
                self.symbol_table[-1][variable_name] = VarSymbol(variable_name, value_type)
            else:
                raise ValueError("Objetivo de asignacion no soportado")

    # Define el metodo visit_Call para visitar nodos de llamadas a funciones.
    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            func_name = node.func.id  # Obtiene el nombre de la funcion llamada.
            # Comprueba si la funcion llamada es una funcion incorporada en Python.
            if func_name not in dir(__builtins__):
                raise ValueError(f"Funcion no definida: '{func_name}'")
        for arg in node.args:
            self.visit(arg)  # Visita los argumentos de la llamada.

    # Define el metodo visit_BinOp para visitar nodos de operaciones binarias.
    def visit_BinOp(self, node):
        self.visit(node.left)  # Visita el operando izquierdo.
        self.visit(node.right)  # Visita el operando derecho.
        left_type = self.get_value_type(node.left)  # Obtiene el tipo del operando izquierdo.
        right_type = self.get_value_type(node.right)  # Obtiene el tipo del operando derecho.
        # Comprueba si hay una coincidencia de tipos valida para la operacion binaria.
        if (left_type, right_type) not in [(int, float), (float, int), (int, int), (float, float), (str, str)]:
            raise ValueError(f"Coincidencia de tipos incorrecta en operacion binaria: {left_type} y {right_type}")

    # Define el metodo get_value_type para obtener el tipo de un nodo.
    def get_value_type(self, node):
        if isinstance(node, ast.Name):
            if node.id in self.symbol_table[-1]:
                return self.symbol_table[-1][node.id].type  # Devuelve el tipo de la variable desde la tabla de simbolos.
            else:
                raise ValueError(f"Variable no definida: '{node.id}'")
        elif isinstance(node, ast.BinOp):
            left_type = self.get_value_type(node.left)  # Obtiene el tipo del operando izquierdo.
            right_type = self.get_value_type(node.right)  # Obtiene el tipo del operando derecho.
            # Comprueba si hay una coincidencia de tipos valida para la operacion binaria.
            if left_type == right_type or (left_type, right_type) in [(int, float), (float, int)]:
                return float
            else:
                raise ValueError(f"Coincidencia de tipos incorrecta en operacion binaria: {left_type} y {right_type}")
        elif isinstance(node, ast.Num):
            return int if isinstance(node.n, int) else float  # Devuelve int o float segun el tipo del numero.
        elif isinstance(node, ast.Str):
            return str  # Devuelve str para cadenas.
        else:
            raise TypeError(f"Nodo desconocido {node}")  # Lanza un error si se encuentra un nodo desconocido.

# Define la funcion analyze_semantics para realizar el analisis semantico del archivo especificado.
def analyze_semantics(filename):
    with open(filename, 'r') as file:
        source_code = file.read()  # Lee el codigo fuente del archivo.

    try:
        tree = ast.parse(source_code)  # Analiza el codigo fuente en un arbol sintactico abstracto (AST).
        analyzer = SemanticAnalyzer()  # Crea una instancia del analizador semantico.
        analyzer.visit(tree)  # Inicia el proceso de analisis semantico visitando el arbol AST.
        print("Analisis semantico aprobado.")
    except Exception as e:
        print(f"Fallo en el analisis semantico: {e}")

# La siguiente linea ejecuta la funcion analyze_semantics cuando se ejecuta este script como el programa principal.
if __name__ == "__main__":
    filename = "test.py"  # Nombre del archivo que se va a analizar semanticamente.
    analyze_semantics(filename)  # Llama a la funcion analyze_semantics para realizar el analisis semantico.

