"""The pages of the New dataset wizard, in order"""

from .acquisition import AcquisitionPage
from .dataset import DatasetPage
from .labels import LabelsPage
from .review import ReviewPage
from .sources import SourcesPage

PAGES = (DatasetPage, AcquisitionPage, SourcesPage, LabelsPage, ReviewPage)
