# This is the root of the talos module.
import warnings

# Suppress a specific UserWarning from NLTK
warnings.filterwarnings(
    "ignore",
    message="A NumPy version.*is required for this version of SciPy.*",
    category=UserWarning,
    module="nltk.metrics.association",
)
