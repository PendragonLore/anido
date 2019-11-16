# -*- coding: utf-8 -*-

import click


class RangeType(click.ParamType):
    name = "range"

    def __init__(self, sep=":"):
        self._sep = sep

    def convert(self, value, param, ctx):
        try:
            ret = map(int, value.split(self._sep, 2))
        except ValueError:
            return self.fail("An invalid integer was provided in the range.", param, ctx)

        return range(*ret)
