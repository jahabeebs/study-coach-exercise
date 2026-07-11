# Lesson 5: Programming Languages

## Machine Code and Assembly

A CPU executes only machine code: binary instructions specific to its design. Writing
machine code directly is error-prone and tedious. Assembly language improves on this
slightly by giving instructions short names (like ADD and MOV), with an assembler
translating those names into machine code. Assembly is still low-level: one line of
assembly corresponds to one machine instruction.

## High-Level Languages

High-level programming languages such as Python, Java, and JavaScript let programmers
express logic in a form closer to human language, with variables, functions, and
control structures. One line of a high-level language may correspond to many machine
instructions. High-level code is also portable: the same program can run on different
kinds of CPU, because translation to machine code happens separately for each.

## Compilers

A compiler translates an entire program from a high-level language into machine code
before the program runs. The output is an executable file that can run repeatedly
without further translation. Compiled languages such as C and C++ typically produce
fast programs, and the compiler catches many errors before the program ever runs. The
cost is an extra build step: after every change, the program must be recompiled.

## Interpreters

An interpreter translates and executes a program line by line while the program runs,
with no separate build step. Interpreted languages such as Python offer a faster
write-and-run cycle, which makes them popular for learning and rapid development. The
tradeoff is speed: interpreting each line during execution is slower than running
machine code produced ahead of time. Some languages blend both approaches — Java
compiles to an intermediate bytecode that a virtual machine then executes.

## Syntax and Semantics

Syntax is the set of rules describing what programs are legally written in a language;
semantics is what those programs mean when executed. A missing parenthesis is a syntax
error: the program cannot be translated at all. A program that runs but computes the
wrong answer has a semantic error — often called a logic bug. Compilers and
interpreters catch syntax errors automatically; finding logic bugs requires testing
and careful reasoning.

## A First Look at Python

Python is a high-level, interpreted language known for readable syntax. A Python
program that prints a greeting is a single line: `print("Hello, world!")`. Python uses
indentation to group statements, which enforces readable structure. Its large standard
library and gentle learning curve have made it one of the most widely used first
languages in education.
