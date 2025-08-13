from abc import ABC, abstractmethod
from typing import Generic, TypeVar

InputDTO = TypeVar("InputDTO")
OutputDTO = TypeVar("OutputDTO")


class Lifecheck(ABC, Generic[InputDTO, OutputDTO]):
    @abstractmethod
    async def __call__(self, data: InputDTO) -> OutputDTO:
        raise NotImplementedError
