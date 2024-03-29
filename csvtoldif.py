#!/usr/bin/env python3
# encoding: utf-8 (as per PEP 263)

import sys
import os
import fileinput
import csv
import base64
from textwrap import TextWrapper

LINELENGTH = 76

SEPARATOR = ';'
JOINER = '|'
QUOTECHAR = '"'

"""
Final structure:
    dn: uid=doejohnn,ou=members,ou=people,dc=zimvm,dc=fsinfo,dc=fim,dc=uni-passa
     u,dc=de
    cn: John Doe
    displayname: JohnD

    dn: ...
"""

def is_ascii(s):
    return all(ord(char) < 128 for char in s)

def main():
    wrapper = TextWrapper(width=76, expand_tabs=False,
            replace_whitespace=False, drop_whitespace=False, initial_indent='',
            subsequent_indent=' ', break_long_words=True,
            break_on_hyphens=False)
    csvreader = csv.reader(fileinput.input(mode='r'), delimiter=SEPARATOR, quotechar=QUOTECHAR, quoting=csv.QUOTE_ALL)
    first = True
    for row in csvreader:
        if first:
            attrs = row
            dn_index = attrs.index('dn')
            first = False

        else:
            line = 'dn: %s\n' % (row[dn_index])
            sys.stdout.write('\n'.join(wrapper.wrap(line)))

            for idx, attr in enumerate(attrs):
                values = row[idx]

                for value in values.split(JOINER):
                    if value == '':
                        # skip undefined attributes
                        continue

                    if attr == 'dn':
                        # skip dn attribute (we already included it in the beginning)
                        continue

                    is_base64 = False

                    if value.startswith('FILE='):
                        filename = value[len('FILE='):]
                        with open(filename, 'rb') as f:
                            value = f.read()
                        try:
                            value = value.decode('ascii')
                        except UnicodeDecodeError:
                            is_base64 = True
                            value = base64.b64encode(value).decode('ascii')
                    else:
                        if not is_ascii(value):
                            is_base64 = True
                            value = base64.b64encode(value.encode('utf8')).decode('ascii')

                    if is_base64:
                        line = '%s:: %s\n' % (attr, value)
                    else:
                        line = '%s: %s\n' % (attr, value)
                    sys.stdout.write('\n'.join(wrapper.wrap(line)))

            sys.stdout.write('\n')

    return 0

    data = {}
    attrs = set()
    charset = set()
    current_dn = ''
    fp = filepeek()
    while True:
        line = fp.next()
        if line is None:
            break

        if not line:
            # end of dn block
            current_dn = ''
            continue

        if line.lstrip().startswith('#'):
            # skip comment line
            continue

        if line.startswith('version: '):
            # skip version line
            continue

        key, value = line.split(': ', 1)
        is_b64 = key.endswith(':')
        key = key.rstrip(':')

        full_value = value
        while fp.peek().startswith(' '):
            full_value += fp.next()[1:]

        if is_b64:
            full_value = base64.b64decode(full_value)

        attrs.add(key)

        if key == 'dn':
            current_dn = full_value
            data[current_dn] = {}

        if not current_dn:
            raise Exception('Non-dn attribute "%s" while not inside a dn block!' % (key))

        if key not in data[current_dn]:
            data[current_dn][key] = []

        if len(full_value) < 500:
            if type(full_value) is bytes:
                full_value = full_value.decode('utf8')

            store_value = full_value

        else:
            # too large for CSV output, write to file instead

            # find unused filename
            fileid = 0
            while True:
                filename = 'dn=%s,attr=%s,id=%d' % (current_dn, key, fileid)
                if not os.path.exists(filename):
                    break
                fileid += 1

            with open(filename, 'wb') as f:
                f.write(full_value)

            store_value = 'FILE=' + filename

        data[current_dn][key] += [store_value]
        charset.update(set(store_value))

    usable_chars = set(string.printable) - set(string.whitespace)
    available_chars = usable_chars - charset
    sys.stderr.write('The following characters DO NOT appear in the dataset (i.e. they can be freely used as separators etc):\n')
    sys.stderr.write('%s\n' % (' '.join(sorted(available_chars))))

    attrs = list(sorted(attrs))

    first = True
    for attr in attrs:
        if not first:
            sys.stdout.write(separator)
        sys.stdout.write(attr)
        first = False

    sys.stdout.write('\n')

    for entry in data:
        first = True
        for attr in attrs:
            if not first:
                sys.stdout.write(separator)
            if attr in data[entry]:
                sys.stdout.write(strdelimiter)
                sys.stdout.write(
                        joiner.join(
                            data[entry][attr]
                        )
                )
                sys.stdout.write(strdelimiter)
            first = False
        sys.stdout.write('\n')


if __name__ == '__main__':
    main()