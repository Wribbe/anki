#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re

lines =  [line.strip('\n') for line in open(sys.argv[1]).readlines()]

#remove indentation
lines = [re.sub(r'^\s*', '', line) for line in lines]

#remove comments
lines = [line for line in lines if not line.startswith('#')]

data = []

def compress_empty_lines(lines):
    last_was_empty = False
    seen_non_empty = False
    new_lines = []
    for line in lines:
        if not line.strip():
            if not seen_non_empty or last_was_empty:
                continue
            last_was_empty = True
            new_lines.append(line)
        else:
            new_lines.append(line)
            last_was_empty = False
            seen_non_empty = True
    return new_lines

def remove_comment_blocks(lines):
    new_lines = []
    ignore = False
    for line in lines:
        if '/*' in line:
            ignore = True
        if '*/' in line:
            ignore = False
            continue
        if ignore:
            continue
        else:
            new_lines.append(line)
    return new_lines

def tag(string):
    return "<div>{}</div>".format(string)

def fig(string):
    figurename = string.split("{")[-1].replace("}",'')
    return '<img src="{}" />'.format(figurename)


lines = remove_comment_blocks(lines)
lines = compress_empty_lines(lines)

current_question = []
current_text = []

for line in lines:
    if line == "/split":
        line = 3*"="
    if "fig{" in line:
        line = fig(line)
    if not line.strip():
        question = "".join(current_question)
        answer = "".join(current_text)
        data.append((question, answer))
        current_question = []
        current_text = []
    elif line.startswith('--'):
        current_question = current_text
        current_text = []
    else:
        current_text.append(tag(line))

if current_text:
    question = "".join(current_question)
    answer = "".join(current_text)
    data.append((question, answer))

for question, answer in data:
    print("{}\t{}".format(question, answer))
