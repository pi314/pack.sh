from abc import ABCMeta, abstractmethod
from shutil import which


def abstract_property(p):
    return property(abstractmethod(p))


class BaseArchiver(metaclass=ABCMeta):
    @abstract_property
    def exts(cls):
        ...

    @abstract_property
    def utils(cls):
        ...

    @property
    def lacked_utils(self):
        return list(filter(lambda x: which(x) is None, self.utils))

    @property
    def why(self):
        if self.lacked_utils:
            return '(need ' + ', '.join(self.lacked_utils) + ')'

        return ''

    def archive(self, args):
        raise NotImplementedError(type(self).__name__ + '.archive()')
