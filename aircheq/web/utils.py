
def strip_underscore_attr(model_vars):
    return { k : v for k, v in model_vars.items() if not k.startswith("_")}

def program_to_dict(program):
    p = vars(program)

    p['duration'] = int(program.duration.total_seconds() * 1000)
    # exclude properties starting with "_"
    return strip_underscore_attr(p)

def strip_for_guide(program_dict):
    p = program_dict.copy()

    targets = ("end", "channel", "service", "is_recorded")
    for key in targets:
        p.pop(key)

    return p
