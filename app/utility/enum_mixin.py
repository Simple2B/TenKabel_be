import enum


class IndexableStringEnum(
    str,
    enum.Enum,
):
    @classmethod
    def get_index(cls, value: str):
        return list(cls).index(value)
