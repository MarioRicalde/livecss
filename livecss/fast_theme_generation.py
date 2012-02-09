__all__ = ['generate_theme_file']


def dict_to_plist(dictionary):
    """ Convert dict object to xml plist format """
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


def seek_until(fo, until):
    """ Find `until` in `fo`

    :param fo: file object
    :param until: word to Find
    :return: found word position in file

    """
    # reverse the searching word
    # because we read file from the end
    until = until[::-1]
    offset = -1
    fo.seek(offset, 2)
    word = ""
    while word != until:
        offset = offset - 1
        try:
            fo.seek(offset, 2)
            # read one character by one
            char = fo.read(1)
            if char == '\n' or char == ' ':  # word deviders
                word = ""
            else:
                word += char
        except IOError:  # not found
            return
    return fo.tell() - 1


def generate_theme_file(theme_file_path, dict_seq, new_theme_file_path):
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
         