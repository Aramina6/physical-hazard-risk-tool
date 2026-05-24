"""Physical Hazard package.

This package contains the four physical risk modules:
- earthquakes
- tropical_cyclones
- space_hazards
- nfip_insurance

These are kept separate from the core financial factor modeling code
so the project can scale cleanly as a hybrid physical + financial risk platform.
"""

from . import earthquakes
from . import tropical_cyclones
from . import space_hazards
from . import nfip_insurance

__all__ = ["earthquakes", "tropical_cyclones", "space_hazards", "nfip_insurance"]
