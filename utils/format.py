from __future__ import annotations

import datetime

from typing import Any, Iterable, Optional, Sequence

def truncate_string(value, max_length=128, suffix="..."):
    string_value = str(value)
    string_truncated = string_value[
        : min(len(string_value), (max_length - len(suffix)))
    ]
    suffix = suffix if len(string_value) > max_length else ""
    return string_truncated + suffix


class plural:
    def __init__(self, value: int):
        self.value: int = value

    def __format__(self, format_spec: str) -> str:
        v = self.value
        singular, sep, plural = format_spec.partition('|')
        plural = plural or f'{singular}s'
        if abs(v) != 1:
            return f'{v} {plural}'
        return f'{v} {singular}'


def human_join(seq: Sequence[str], delim: str = ', ', final: str = 'or') -> str:
    size = len(seq)
    if size == 0:
        return ''

    if size == 1:
        return seq[0]

    if size == 2:
        return f'{seq[0]} {final} {seq[1]}'

    return delim.join(seq[:-1]) + f' {final} {seq[-1]}'

class TabularDataError(Exception):
    pass

class TabularData:
    def __init__(self):
        self._widths: list[int] = []
        self._columns: list[str] = []
        self._rows: list[list[str]] = []

    def set_columns(self, columns: list[str]):
        self._columns = columns
        self._widths = [len(c) + 2 for c in columns]

    def add_row(self, row: Iterable[Any]) -> None:
        rows = [str(r) for r in row]
        self._rows.append(rows)
        for index, element in enumerate(rows):
            width = len(element) + 2
            
            if width > self._widths[index]:
                self._widths[index] = width
            if len(rows) != len(self._columns):
                x = self._rows.pop()
                y = len(x) -len(self._columns)
                if y > 0:
                    raise TabularDataError(f'Row has an invalid number of elements. Please add {abs(y)} coloumns')
                else:
                    raise TabularDataError(f'Row has an invalid number of elements. Please remove {abs(y)} coloumns')

    def add_rows(self, rows: Iterable[Iterable[Any]]) -> None:
        for row in rows:
            self.add_row(row)

    def render(self) -> str:
        sep = '+'.join('-' * w for w in self._widths)
        sep = f'+{sep}+'

        to_draw = [sep]

        def get_entry(d):
            elem = '|'.join(f'{e:^{self._widths[i]}}' for i, e in enumerate(d))
            return f'|{elem}|'

        to_draw.append(get_entry(self._columns))
        to_draw.append(sep)

        for row in self._rows:
            to_draw.append(get_entry(row))

        to_draw.append(sep)
        return '\n'.join(to_draw)


def format_dt(dt: datetime.datetime, style: Optional[str] = None) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)

    if style is None:
        return f'<t:{int(dt.timestamp())}>'
    return f'<t:{int(dt.timestamp())}:{style}>'


def tick(opt: Optional[bool], /) -> str:
    lookup = {
        True: '<:greenTick:330090705336664065>',
        False: '<:redTick:330090723011592193>',
        None: '<:greyTick:563231201280917524>',
    }
    return lookup.get(opt, '<:redTick:330090723011592193>')


# row = [
#     ['hi', 'hello', 'hey', 'yo', 'sup', 'hi', 'hello', 'hey', 'yo', 'sup'],
# ]

# x = TabularData()
# x.set_columns(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j'])
# x.add_rows(row)
# print(x.render())

# +----+-------+-----+----+-----+----+-------+-----+----+-----+
# | a  |   b   |  c  | d  |  e  | f  |   g   |  h  | i  |  j  |
# +----+-------+-----+----+-----+----+-------+-----+----+-----+
# | hi | hello | hey | yo | sup | hi | hello | hey | yo | sup |
# +----+-------+-----+----+-----+----+-------+-----+----+-----+


# +-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
# |  a  |  b  |  c  |  d  |  e  |  f  |  g  |  h  |  i  |  j  |
# +-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
# |  1  |  2  |  3  |  4  |  5  |  6  |  7  |  8  |  9  | 10  |
# | 11  | 12  | 13  | 14  | 15  | 16  | 17  | 18  | 19  | 20  |
# +-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+