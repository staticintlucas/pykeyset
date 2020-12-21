# coding: utf-8

from ..utils.error import error

def load_font(ctx, *args):

    if len(args) == 0:
        error(ctx.conf, f"not enough arguments for command 'load font' in '{ctx.name}'")
    elif len(args) > 1:
        error(ctx.conf, f"too many arguments for command 'load font' in '{ctx.name}'")
