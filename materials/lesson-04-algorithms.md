# Lesson 4: Algorithms

## What Is an Algorithm

An algorithm is a precise, step-by-step procedure for solving a problem. A recipe is a
useful analogy: given ingredients (input), following the steps produces a dish
(output). For a procedure to be an algorithm, its steps must be unambiguous, it must
finish after a finite number of steps, and it must produce a correct result for every
valid input. The same algorithm can be expressed in English, in pseudocode, or in any
programming language.

## Pseudocode

Pseudocode describes an algorithm in structured, language-neutral text. It uses
constructs such as IF/ELSE for decisions, WHILE and FOR for repetition, and variables
for storing values, without the exact syntax of any programming language. Pseudocode
lets people design and discuss an algorithm before writing real code.

## Linear Search

Linear search finds a target value in a list by checking each element one at a time,
from the first to the last, until the target is found or the list is exhausted. In the
worst case, linear search examines every element. Its advantage is simplicity: it
works on any list, sorted or not.

## Binary Search

Binary search finds a target value in a sorted list by repeatedly halving the search
range. It compares the target to the middle element: if the target is smaller, the
search continues in the left half; if larger, in the right half. Each comparison
eliminates half the remaining elements, so a list of one million items needs at most
about twenty comparisons. Binary search requires the list to be sorted in advance.

## Sorting

Sorting arranges a list into order. Bubble sort, a simple teaching algorithm,
repeatedly steps through the list and swaps adjacent elements that are out of order;
it is easy to understand but slow on large lists. Merge sort divides the list in half,
sorts each half, and merges the sorted halves; it is dramatically faster on large
inputs. Efficient sorting matters because sorted data enables fast operations like
binary search.

## Comparing Algorithm Efficiency

Computer scientists compare algorithms by how their running time grows with input
size, written in Big-O notation. Linear search is O(n): doubling the list doubles the
worst-case work. Binary search is O(log n): doubling a sorted list adds only one more
comparison. Bubble sort is O(n²), while merge sort is O(n log n). For small inputs the
difference barely matters, but at scale the growth rate dominates everything else.
