class textf:
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

    def style(text, s):
        return '{}{}{}'.format(s, text, textf.END)
