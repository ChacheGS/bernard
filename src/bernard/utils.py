# coding: utf-8
import importlib
import asyncio
from collections import Sequence, Mapping
from typing import Text, Coroutine, Any, Union, Dict, Iterator


def import_class(name: Text) -> type:
    """
    Import a class based on its full name.

    :param name: name of the class
    """

    parts = name.split('.')
    module_name = parts[:-1]
    class_name = parts[-1]
    module_ = importlib.import_module('.'.join(module_name))
    return getattr(module_, class_name)


def run(task: Coroutine) -> Any:
    """
    Run a task in the default asyncio look.

    :param task: Task to run
    """

    return asyncio.get_event_loop().run_until_complete(task)


async def run_or_return(task: Union[Coroutine, Any]):
    try:
        task = asyncio.ensure_future(task)
        return await task
    except TypeError:
        return task


class RoList(Sequence):
    """
    Wrapper around a list to make it read-only
    """

    def __init__(self, data: Sequence, forgive_type=False):
        """
        Store data we're wrapping
        """
        self._data = data
        self._forgive_type = forgive_type

    def __getitem__(self, index: int) -> Any:
        """
        Proxy to data's get item
        """
        return make_ro(self._data[index], self._forgive_type)

    def __len__(self):
        """
        Proxy to data's length
        """
        return len(self._data)


class RoDict(Mapping):
    """
    Wrapper around a dict to make it read-only.
    """

    def __init__(self, data: Dict[Text, Any], forgive_type=False):
        self._data = data
        self._forgive_type = forgive_type

    def __getitem__(self, key: Text) -> Any:
        """
        Gets the item from data while making it read-only first
        """

        return make_ro(self._data[key], self._forgive_type)

    def __len__(self) -> int:
        """
        Proxy to data's length
        """

        return len(self._data)

    def __iter__(self) -> Iterator[Any]:
        """
        Proxy to data's iterator
        """

        return iter(self._data)


# noinspection PyTypeChecker
def make_ro(obj: Any, forgive_type=False):
    """
    Make a json-serializable type recursively read-only

    :param obj: Any json-serializable type 
    :param forgive_type: If you can forgive a type to be unknown (instead of
                         raising an exception)
    """

    if isinstance(obj, (str, bytes, int, float, bool, RoDict, RoList)) \
            or obj is None:
        return obj
    elif isinstance(obj, Mapping):
        return RoDict(obj, forgive_type)
    elif isinstance(obj, Sequence):
        return RoList(obj, forgive_type)
    elif forgive_type:
        return obj
    else:
        raise ValueError('Trying to make read-only an object of type "{}"'
                         .format(obj.__class__.__name__))