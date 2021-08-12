from typing import Optional


REPL_LIST = [("\r", ""), ("\n ", "\n"), (" \n", "\n"), ("  ", " "), ("\t\n", "\n")]
STRIP_CHARS = "\r "


def replacer(text: str, l_repl: Optional[list] = None, s_strip: str = "\n\r\t "):
    if s_strip is not None:
        text = text.strip(s_strip)
    if l_repl is not None:
        for item in l_repl:
            text = text.replace(item[0], item[1])
    return text
