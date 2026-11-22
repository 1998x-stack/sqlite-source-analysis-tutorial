#!/usr/bin/env python3
"""A toy shift/reduce arithmetic parser, deliberately NOT SQLite's Lemon parser."""
import re
SOURCE = "1+2+3"
assert re.fullmatch(r"\d+(?:\+\d+)*", SOURCE)
tokens = re.findall(r"\d+|\+", SOURCE)
stack: list[tuple[str, int | None]] = []
for word in tokens:
    if word == "+":
        stack.append(("PLUS", None))
        print("shift PLUS", stack)
        continue
    value = int(word)
    stack.append(("NUM", value))
    print("shift NUM", stack)
    stack[-1] = ("term", value)
    print("reduce NUM -> term", stack)
    if len(stack) >= 3 and [x[0] for x in stack[-3:]] == ["expr", "PLUS", "term"]:
        a = stack[-3][1]
        assert isinstance(a, int)
        stack[-3:] = [("expr", a + value)]
        print("reduce expr PLUS term -> expr", stack)
    else:
        stack[-1] = ("expr", value)
        print("reduce term -> expr", stack)
assert len(stack) == 1 and stack[0] == ("expr", 6), stack
print("value:", stack[0][1])
