memory = []

def add_memory(q,a):
    memory.append({"q":q,"a":a})

def get_memory():
    return memory[-3:]