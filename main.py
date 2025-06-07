import tkinter as tk
from tkinter import messagebox, scrolledtext
import re

# analisador lexico --------------------------------------------------------------------------
def tokenize(code):
    token_specification = [
        ('NUMBER',   r'\d+'),
        ('STRING',   r'"[^"\n]*"|\'[^\'\n]*\''),
        ('ASSIGN',   r'='),
        ('PRINT',    r'print'),
        ('IF',       r'if'),
        ('ELSE',     r'else'),
        ('WHILE',    r'while'),
        ('ID',       r'[A-Za-z_]\w*'),
        ('RELOP',    r'==|!=|<=|>=|<|>'),
        ('OP',       r'[+\-*/()]'),
        ('LBRACE',   r'\{'),
        ('RBRACE',   r'\}'),
        ('NEWLINE',  r'\n'),
        ('SKIP',     r'[ \t]+'),
        ('MISMATCH', r'.'),
    ]

    tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specification)
    tokens = []
    line_num = 1
    line_start = 0
    for mo in re.finditer(tok_regex, code):
        kind = mo.lastgroup
        value = mo.group()
        column = mo.start() - line_start
        if kind == 'NEWLINE':
            line_num += 1
            line_start = mo.end()
        elif kind == 'SKIP':
            continue
        elif kind == 'MISMATCH':
            raise SyntaxError(f"Caractere inesperado {value!r} na linha {line_num}")
        else:
            tokens.append((kind, value, line_num))
    return tokens

# parser e interpretador ---------------------------------------------------------------------------
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.variables = {}
        self.output = ""

    def current_line(self):
        return self.tokens[self.pos][2] if self.pos < len(self.tokens) else -1

    def match(self, expected_type):
        if self.pos < len(self.tokens) and self.tokens[self.pos][0] == expected_type:
            val = self.tokens[self.pos][1]
            self.pos += 1
            return val
        raise SyntaxError(f"Esperado: {expected_type} na linha {self.current_line()}")

    def match_peek(self, kind):
        return self.pos < len(self.tokens) and self.tokens[self.pos][0] == kind

    def parse_expression(self):
        return self.parse_term()

# Árvore Sintática --------------------------------------------------------------------------
    def parse_term(self):
        node = self.parse_factor()
        while self.pos < len(self.tokens) and self.tokens[self.pos][1] in ('+', '-'):
            op = self.tokens[self.pos][1]
            self.pos += 1
            right = self.parse_factor()
            node = (op, node, right)
        return node

    def parse_factor(self):
        node = self.parse_atom()
        while self.pos < len(self.tokens) and self.tokens[self.pos][1] in ('*', '/'):
            op = self.tokens[self.pos][1]
            self.pos += 1
            right = self.parse_atom()
            node = (op, node, right)
        return node

    def parse_atom(self):
        tok_type, tok_val, _ = self.tokens[self.pos]
        if tok_type == 'NUMBER':
            self.pos += 1
            return int(tok_val)
        elif tok_type == 'STRING':
            self.pos += 1
            return tok_val.strip('"\'')
        elif tok_type == 'ID':
            self.pos += 1
            return ('var', tok_val)
        elif tok_val == '(':
            self.pos += 1
            expr = self.parse_expression()
            self.match('OP')
            return expr
        else:
            raise SyntaxError(f"Token inesperado: {tok_val} na linha {self.current_line()}")

    def eval_node(self, node):
        if isinstance(node, int) or isinstance(node, str):
            return node
        elif isinstance(node, tuple):
            if node[0] == 'var':
                return self.variables.get(node[1], 0)
            left = self.eval_node(node[1])
            right = self.eval_node(node[2])
            if node[0] == '+':
                return left + right
            elif node[0] == '-':
                return left - right
            elif node[0] == '*':
                return left * right
            elif node[0] == '/':
                return left / right
        raise ValueError("Nó inválido")

    def parse_condition(self):
        left = self.parse_expression()
        op = self.match('RELOP')
        right = self.parse_expression()
        return self.eval_condition(op, left, right)

    def eval_condition(self, op, left, right):
        if isinstance(left, tuple): left = self.eval_node(left)
        if isinstance(right, tuple): right = self.eval_node(right)
        return {
            '==': left == right,
            '!=': left != right,
            '<':  left < right,
            '>':  left > right,
            '<=': left <= right,
            '>=': right >= left,
        }[op]

    def eval_condition_from(self, pos):
        old_pos = self.pos
        self.pos = pos
        result = self.parse_condition()
        self.pos = old_pos
        return result

    def skip_block(self):
        depth = 1
        while self.pos < len(self.tokens):
            if self.tokens[self.pos][0] == 'LBRACE':
                depth += 1
            elif self.tokens[self.pos][0] == 'RBRACE':
                depth -= 1
                if depth == 0:
                    break
            self.pos += 1

    def statement(self):
        if self.match_peek('ID'):
            var_name = self.match('ID')
            self.match('ASSIGN')
            expr = self.parse_expression()
            self.variables[var_name] = self.eval_node(expr)
        elif self.match_peek('PRINT'):
            self.match('PRINT')
            if self.match_peek('OP') and self.tokens[self.pos][1] == '(':
                self.pos += 1
                expr = self.parse_expression()
                self.match('OP')  # ')'
            else:
                expr = ('var', self.match('ID'))
            self.output += f"{self.eval_node(expr)}\n"
        elif self.match_peek('IF'):
            self.match('IF')
            cond = self.parse_condition()
            self.match('LBRACE')
            if cond:
                while not self.match_peek('RBRACE'):
                    self.statement()
                self.match('RBRACE')
                if self.match_peek('ELSE'):
                    self.match('ELSE')
                    self.match('LBRACE')
                    self.skip_block()
                    self.match('RBRACE')
            else:
                self.skip_block()
                self.match('RBRACE')
                if self.match_peek('ELSE'):
                    self.match('ELSE')
                    self.match('LBRACE')
                    while not self.match_peek('RBRACE'):
                        self.statement()
                    self.match('RBRACE')
        elif self.match_peek('WHILE'):
            self.match('WHILE')
            cond_start = self.pos
            condition = self.parse_condition()
            self.match('LBRACE')
            block_start = self.pos
            while self.eval_condition_from(cond_start):
                self.pos = block_start
                while not self.match_peek('RBRACE'):
                    self.statement()
            self.skip_block()
            self.match('RBRACE')
        else:
            raise SyntaxError(f"Comando inválido na linha {self.current_line()}")

    def run(self):
        while self.pos < len(self.tokens):
            self.statement()

# Compilador -------------------------------------------------------------------------------------
def compilar():
    codigo = entrada.get("1.0", tk.END)
    try:
        tokens = tokenize(codigo)
        parser = Parser(tokens)
        parser.run()
        saida.config(state=tk.NORMAL)
        saida.delete("1.0", tk.END)
        saida.insert(tk.END, parser.output)
        saida.config(state=tk.DISABLED)
    except Exception as e:
        messagebox.showerror("Erro de Compilação", str(e))

# interface ---------------------------------------------------------------------------------
janela = tk.Tk()
janela.title("Compilador Python Educacional")
janela.configure(bg="#1e1e1e")

fonte = ("Consolas", 12)
cor_fundo = "#1e1e1e"
cor_texto = "#d4d4d4"
cor_botao = "#333333"
cor_entrada = "#252526"
cor_saida = "#1e1e1e"

tk.Label(janela, text="Código:", bg=cor_fundo, fg=cor_texto, font=fonte).pack(anchor="w", padx=10, pady=(10, 0))

entrada = scrolledtext.ScrolledText(janela, height=12, width=70, bg=cor_entrada, fg=cor_texto, insertbackground="white", font=fonte)
entrada.pack(padx=10)

btn = tk.Button(janela, text="Compilar", command=compilar, bg=cor_botao, fg=cor_texto, font=fonte, relief=tk.FLAT)
btn.pack(pady=10)

tk.Label(janela, text="Saída:", bg=cor_fundo, fg=cor_texto, font=fonte).pack(anchor="w", padx=10)
saida = scrolledtext.ScrolledText(janela, height=8, width=70, bg=cor_saida, fg=cor_texto, state=tk.DISABLED, font=fonte)
saida.pack(padx=10, pady=(0, 10))

janela.mainloop()