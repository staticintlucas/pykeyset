def as_svg(ctx, filename):
    """save the generated graphic as an SVG graphic"""

    raise NotImplementedError


def as_png(ctx, filename):
    """save the graphic as a PNG image (requires Cairo)"""

    raise NotImplementedError


def as_pdf(ctx, filename):
    """save the graphic as a PDF file (requires Cairo)"""

    raise NotImplementedError


def as_ai(ctx, filename):
    """save the graphic as an AI file (experimental; requires Cairo)"""

    raise NotImplementedError
