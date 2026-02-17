from typing import TypeVar, Type, overload

T = TypeVar('T')

class ResourceRegistry:
    """Lightweight resource storage for global/shared objects."""

    def __init__(self):
        self._data = {}

    def register(self, resource: T) -> None:
        """Register resource using its type as key."""
        key = type(resource)
        self._data[key] = resource

    def get(self, resource_type: Type[T]) -> T:
        """Get resource by type. Raises KeyError if not found."""
        if resource_type not in self._data:
            raise KeyError(f"Resource {resource_type.__name__} not found")
        return self._data[resource_type]

    def get_or(self, resource_type: Type[T], default: T) -> T:
        """Get resource by type with default fallback."""
        return self._data.get(resource_type, default)

    def has(self, resource_type: Type[T]) -> bool:
        return resource_type in self._data

    def all(self):
        return dict(self._data)
