import enum


class IndexableStringEnum(
    str,
    enum.Enum,
):
    @classmethod
    def get_index(cls, value: str):
        return list(cls).index(value)

    def next(self):
        return list(self.__class__)[self.get_index(self.value) + 1]
