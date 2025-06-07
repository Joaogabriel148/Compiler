<h1 align="center"> Compiler</h1>

## :memo: Descrição
Projeto criado para a matéria de Códigos de Alta Performance Web. sites de artes.

## :books: Contextualização
* <b>Contextualização </b>: A aplicação em si e um compilador de codigos que tem como funcionalidades: Análise Léxica, Análise Sintática e Análise Semântica

## :wrench: Tecnologias utilizadas
* Python
* Tkinter

## : Interface Gráfica
Interface gráfica criada a partir de uma biblioteca do python chamada de Tkinter
<img src='img\Captura de tela 2025-06-03 143900.png'>

## :game_die: Etapa Das Análises
- Análise Léxica
  - Divide o código-fonte em tokens, reconhecendo números, strings, operadores, identificadores, palavras-chave (print, if, else, while), etc.
  
```python
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

```

- Análise Sintática
  - Verifica a estrutura gramatical dos comandos, garantindo que a ordem dos tokens siga regras da linguagem.
  
```python
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
```
- Análise Semântica
  - O que faz: Verifica se as operações fazem sentido, ou seja, se os significados estão corretos.
  
```python
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
```

## :handshake: Colaboradores
<table>
  <tr>
    <td align="center">
      <a href="https://github.com/Joaogabriel148">
        <sub>
          <b>Joaogabriel148</b>
        </sub>
      </a>
    </td>
  </tr>
</table>