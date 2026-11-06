"""Primary registry adapters that return first-class evidence objects."""

from .clinical_trials import fetch_trial_objects
from .datacite import fetch_dataset_objects
from .open_targets import fetch_entity_objects

__all__ = ["fetch_dataset_objects", "fetch_entity_objects", "fetch_trial_objects"]
