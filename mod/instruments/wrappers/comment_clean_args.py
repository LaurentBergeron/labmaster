with open("dll_AgM8190.py", "r") as f1:
    contents = f1.read()
    with open("dll_AgM8190_new.py", "w") as f2:
        for line in contents.split("\n"):
            if line.startswith("    args = clean_args"):
                f2.write("    args = check_args"+line[21:]+"\n")
            else:
                f2.write(line+"\n")