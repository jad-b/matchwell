"""
Contains the interface for pulling in new data.
"""
import abc


class Sourcerer(abc.ABC):
    """Sourcerer's can pull data from their embedded data source."""
    #: A one-word attributive name for this source of data, suitable for
    # grouping.
    name = None

    @abc.abstractmethod
    def pull(self, **kwargs):
        """Retrieve updates from the data source.

        Returns:
            A new :class:`pandas.DataFrame`, of only this source's type.
        """
        pass
