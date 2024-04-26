from abc import ABC, abstractmethod
from typing import Any


class Exportable(ABC):
    @abstractmethod
    def to_csv(self) -> dict[str, Any]: ...
