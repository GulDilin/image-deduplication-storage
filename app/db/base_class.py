from typing import Any

from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:
    id: Any
    __name__: str

    # Generate __tablename__ automatically
    # SomeClassName -> some_class_name
    @declared_attr
    def __tablename__(cls) -> str:  # noqa
        parts = []
        part = ""
        is_previous_upper = True
        for c in cls.__name__:
            is_upper = c.lower() != c
            if is_upper and not is_previous_upper:
                parts.append(part)
                part = ""
            is_previous_upper = is_upper
            part += c.lower()
        parts.append(part)
        return "_".join([p for p in parts if p])

    def __str__(self) -> str:
        return str(self.id)
