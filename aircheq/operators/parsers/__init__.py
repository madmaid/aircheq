import aircheq.operators.parsers
from . import radiko
from . import nhk_api as radiru
from . import agqr
# from . import syobocal_agqr as agqr

__all__ = ['agqr', 'radiko', 'radiru']
modules = (agqr, radiko, radiru)
