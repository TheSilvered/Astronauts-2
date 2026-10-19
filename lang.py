import lang_attrs

language = lang_attrs.Language

def load_txt(
   acronym: str,
   lang_dir: str = "langs",
   encoding: str = "utf-8",
   log: bool = True) -> lang_attrs.Language:

    global language

    # Resets all attributes
    language = lang_attrs.Language

    file = open(f"{lang_dir}/{acronym}.lang", "r", encoding=encoding)
    sets = []
    attr = ""
    get_text_local = None
    get_text_abs = None
    def_after_attr = None
    prev_invalid_attr = ""

    for l_no, l in enumerate(file):
        for idx, char in enumerate(l):
            if char != " ":
                l = l[idx:]
                break

        l = l.replace("'", "\\'")

        if l[:2] == "::": continue

        elif l[:2] == "!=":
            if l[2:-1].lower() != encoding.lower():
                return load_txt(acronym, lang_dir, l[2:-1], log)
            continue

        elif l[:1] == "$":
            set_count = -1

            for idx, char in enumerate(l):
                if char != "$":
                    l = l[idx:]
                    break
                set_count += 1

            if set_count > len(sets):
                raise SyntaxError(f"Accessed child set with no parent "
                                  f"({l[:-1]}) at line {l_no}")

            sets = sets[:set_count]
            if l[:-1] != "!": sets.append(l[:-1])
            continue

        elif l[:1] == "@":
            has_value = l[1:-1].find(":") + 1
            if not has_value:
                attr = l[1:-1]
                continue
            else:
                attr = l[1:has_value]
                def_after_attr = l[has_value + 1:]
                if len(def_after_attr) > 0 and def_after_attr[-1] == "\n":
                    def_after_attr = def_after_attr[:-1]

        elif l[:3] == ".~@":
            l = l.replace(" ", "")
            attr, get_text_local = l[3:-1].split(";")

        elif l[:2] == "~@":
            attr, get_text_abs = l[2:-1].split(";")

        elif l[:1] == "&":
            l = l[1:-1]

        else:
            l = l[:-1] + "\\n"

        try:
            if sets: main_set = ".".join(sets) + "."
            else: main_set = ""

            if get_text_local is not None:
                exec(f"language.{main_set}{attr} +=\
                       language.{main_set}{get_text_local}")
                get_text_local = None
            elif get_text_abs is not None:
                exec(f"language.{main_set}{attr} +=\
                       language.{get_text_abs}")
                get_text_abs = None
            elif def_after_attr is not None:
                exec(f"language.{main_set}{attr} += '{def_after_attr}'")
                def_after_attr = None
            else:
                exec(f"language.{main_set}{attr} += '{l}'")

        except (AttributeError, SyntaxError) as e:
            if prev_invalid_attr != attr:
                attribute = ".".join(sets) + "." + attr
                print(f"Invalid attribute: '@{attribute}' at line {l_no}, {e}")

            # Prevents spam in a multi-line invalid attributes
            prev_invalid_attr = attr

    file.close()

    return language
