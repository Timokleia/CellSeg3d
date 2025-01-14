from abc import ABC, abstractmethod


class ModelTemplate_(ABC):
    use_default_training = True  # not needed for now, will serve for WNet training if added to the plugin
    weights_file = (
        "model_template.pth"  # specify the file name of the weights file only
    )

    @abstractmethod
    def __init__(
        self, input_image_size, in_channels=1, out_channels=1, **kwargs
    ):
        """Reimplement this as needed; only include input_image_size if necessary. For now only in/out channels = 1 is supported."""
        pass

    @abstractmethod
    def forward(self, x):
        """Reimplement this as needed. Ensure that output is a torch tensor with dims (batch, channels, z, y, x)."""
        pass
