#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import re
import subprocess
import shutil
import tempfile

dir_images = ""
current_image = 0
filename = ""
media_path = "/home/steff/.local/share/Anki2/User 1/collection.media"

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

def latex(string):
    global current_image

    def wrap(code):
        return "\documentclass{standalone}"+\
        "\\begin{document}"+\
            "${}$".format(code)+\
        "\end{document}"

    latex_code_find = re.search("\\\\L.*\\\\L", string)
    latex_code = latex_code_find.group().replace("\\L","").strip()

    if not os.path.exists(dir_images):
        os.mkdir(dir_images)

    dir_old = os.getcwd()
    os.chdir(dir_images)
    with open(os.devnull, 'w') as FNULL:
        subprocess.check_call(["pdflatex", wrap(latex_code)],
                               stdout=FNULL,
                               stderr=subprocess.STDOUT)
    output_name = "{}_{:03d}.svg".format(filename.split('.')[0], current_image)
    output_path = os.path.join(media_path, output_name)
    subprocess.check_call(["pdf2svg", "standalone.pdf", output_path])

    img_path = fig(output_name)
    string = string.replace(latex_code_find.group(), img_path)
    current_image += 1
    os.chdir(dir_old)

    return string


def main():

    global filename, dir_images
    filename = sys.argv[1]
    dir_images = tempfile.mkdtemp()

    lines =  [line.strip('\n') for line in open(filename).readlines()]

    #remove indentation
    lines = [re.sub(r'^\s*', '', line) for line in lines]

    #remove comments
    lines = [line for line in lines if not line.startswith('#')]

    data = []
    lines = remove_comment_blocks(lines)
    lines = compress_empty_lines(lines)

    current_question = []
    current_text = []

    for line in lines:
        if line == "/split":
            line = 3*"="
        if "fig{" in line:
            line = fig(line)
        if "\L" in line:
            line = latex(line)
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

    shutil.rmtree(dir_images)

if __name__ == "__main__":
    main()
