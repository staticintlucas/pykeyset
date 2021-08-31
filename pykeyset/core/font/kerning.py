class Kerning:
    def __init__(self, cap_height):

        raise NotImplementedError

    def get(self, lhs: str, rhs: str, size: float) -> float:
        """Returns the kerning between the given pair of glyph names if set, otherwise returns the
        default value of 0"""

        raise NotImplementedError

    def set(self, lhs: str, rhs: str, kerning: float) -> None:
        """Sets the kerning between the given pair of glyph names"""

        raise NotImplementedError

    def delete(self, lhs: str, rhs: str) -> None:
        """Resets the kerning between the given pair of glyph names. This will not modify the
        anything if the kerning between these characters has not been previously set"""

        raise NotImplementedError

    def __len__(self) -> int:
        """Returns the number of kerning pair explicitly set"""

        raise NotImplementedError
