# -*- coding: utf-8 -*-

"""
    livecss.fast_theme_generation
    ~~~~~~~~~


"""


def dict_to_plist(dictionary):
    """Converts dict object to xml plist format"""
    start = '<dict>'
    end = '</dict>'
    out = [start]
    for k, v in dictionary.items():
        # value can  contain any number of nested dicts
        if isinstance(v, dict):
            out.append('<key>%s</key>' % k)
            out.append(dict_to_plist(v))
        else:
            out.append(elem(k, v))
    out.append(end)
    return '\n'.join(out)


def elem(k, v):
    return '<key>%s</key>\n<string>%s</string>' % (k, v)


def seek_until(fileobj, until):
    """Finds `until` in `fileobj`

    :param fileobj: file like object
    :param until: word to find
    :return: found word position in file

    """
    # reverse the searching word
    # because we read file from the end
    until = until[::-1]
    offset = -1
    fileobj.seek(offset, 2)
    word = ""
    while word != until:
        offset = offset - 1
        try:
            fileobj.seek(offset, 2)
            # read one character by one
            char = fileobj.read(1)
            if char == '\n' or char == ' ':  # word deviders
                word = ""
            else:
                word += char
        except IOError:  # not found
            return
    return fileobj.tell() - 1


def generate_theme_file(theme_file_path, dict_seq, new_theme_file_path):
    """Appends `dict_seq` to `new_theme_file_path`, converting it to plist format.

    :param theme_file_path: path to the theme file to read from
    :param dict_seq: list of dictionaries with color definitions
    :param new_theme_file_path: path to the created theme file

    """

    with open(theme_file_path) as f:
        # parse dict objects to plist format
        tempate_to_write = (dict_to_plist(d) for d in dict_seq)
        # find end of colors difinition
        end_pos = seek_until(f, '</array>')
        # text until insertation place
        f.seek(0)
        begin_text = f.read(end_pos)
        # new colors definition plus end of file
        f.seek(end_pos)
        end_text = '\n'.join(tempate_to_write) + f.read()
        new_theme_text = begin_text + end_text

    with open(new_theme_file_path, 'w') as f:
        f.write(new_theme_text)
