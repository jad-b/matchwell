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
    def pull(self, df=None, **kwargs):
        """Retrieve updates from the data source.

        Args:
            df(: class: `pandas.DataFrame`):
                DataFrame to use as a base of reference.
                Not providing one indicates a full copy from the source is to
                be performed, if possible.
        Returns:
            A new :class:`pandas.DataFrame`, of only this source's type.
        """
        pass
