"""
Module for automatically creating the documentation.
This script is called within the makefile.

It creates the subfiles for each method of a class and adjusts the class .rst file.

"""

import os
import glob


def make_docs(file,line):
    f_name = line.split(".")[-1]
    path = "/".join(file.split("/")[:-1])
    path += "/"
    file = file.split("/")[-1]
    # print(path,file,line)
    new_file = ".".join(file.split(".")[:-1])
    new_file += "." + f_name + ".rst"
    # print(new_file)
    if os.path.isfile(path+new_file):
        os.remove(path + new_file)

    with open(path + new_file,"w") as f:
        f.write(f_name + "\n")
        f.write("".join(["=" for i in f_name]) + "\n")
        f.write("\n")

        f.write(".. currentmodule:: " + ".".join(file.split(".")[:3]) + "\n")
        f.write("\n")
        f.write(".. automethod:: " + file.split(".")[3] +"." +  f_name +  "\n")





module_directory = os.path.dirname(os.path.abspath(__file__))
generated_directory = os.path.join(module_directory,"generated")
for file in glob.glob(generated_directory + "/*.rst"):
    class_file = False
    with open(file,"r") as f:

        content = f.read()
        # print(content)
        if "autoclass" in content:
            class_file = True
        else:
            continue

        lines = content.split("\n")
        for line in lines:
            if class_file:

                if "~" in line:
                    line = "  " + line
                    if not "__" in line:
                        # print(line)
                        make_docs(file,line)

    with open(file, "w") as f:
        ind = content.index(".. autosummary::")
        content0 = content[:ind+len("  .. autosummary::")]
        content2 = content[ind+len("  .. autosummary::"):]
        content1 = "     :toctree:\n\n"

        content3 = []

        for line in content2.split("\n"):
            l = "  " + line
            content3.append(l)

        content3 = "\n".join(content3)

        f.write(content0 + content1 + content2)