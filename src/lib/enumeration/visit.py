from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, Any, Dict, List, Tuple, Callable
from logging import Logger


class AbstractVisit(ABC):
    def __init__(self: AbstractVisit, logger: Optional[Logger] = None) -> None:
        self.logger: Logger = logger or Logger(__name__)

    @abstractmethod
    def __call__(self: AbstractVisit, port: int, address: str) -> None | Callable[[], Any]:
        """
        Execute the visit action and assess the web resource.

        Parameters
        ----------
        port: int
            The port number of the web resource.
        address: str
            The IP address of the web resource.

        Returns
        -------
        None | Callable[[], Any]
            If conditions of the connection are not met, `None` is returned. Otherwise, a callable object is returned.

        The callable object returns the result of the visit action. The result is a tuple consisting of the following:
            - Report: A dictionary containing the results of the visit action.
            - Crawlable URLs/Pages. Should include port and address.
        """
        pass
