from pathlib import Path

from napari_cellseg3d._tests.fixtures import (
    LogFixture,
    LossFixture,
    OptimizerFixture,
    WNetFixture,
)
from napari_cellseg3d.code_models.models.model_test import TestModel
from napari_cellseg3d.code_models.workers_utils import TrainingReport
from napari_cellseg3d.code_plugins.plugin_model_training import (
    Trainer,
)
from napari_cellseg3d.config import MODEL_LIST

im_path = Path(__file__).resolve().parent / "res/test.tif"
im_path_str = str(im_path)


def test_supervised_training(make_napari_viewer_proxy):
    viewer = make_napari_viewer_proxy()
    widget = Trainer(viewer)
    widget.log = LogFixture()

    widget.images_filepath = []
    widget.labels_filepaths = []

    assert not widget.check_ready()

    widget.images_filepaths = [im_path_str]
    widget.labels_filepaths = [im_path_str]
    widget.epoch_choice.setValue(1)
    widget.val_interval_choice.setValue(1)

    assert widget.check_ready()

    MODEL_LIST["test"] = TestModel
    widget.model_choice.addItem("test")
    widget.model_choice.setCurrentText("test")
    widget.unsupervised_mode = False
    worker_config = widget._set_worker_config()
    assert worker_config.model_info.name == "test"
    worker = widget._create_supervised_worker_from_config(worker_config)
    worker.config.train_data_dict = [
        {"image": im_path_str, "label": im_path_str}
    ]
    worker.config.val_data_dict = [
        {"image": im_path_str, "label": im_path_str}
    ]
    worker.config.max_epochs = 1
    worker.config.validation_interval = 2
    worker.log_parameters()
    res = next(worker.train())

    assert isinstance(res, TrainingReport)
    assert res.epoch == 0

    widget.worker = worker
    res.show_plot = True
    res.loss_1_values = {"loss": [1, 1, 1, 1]}
    res.loss_2_values = [1, 1, 1, 1]
    widget.on_yield(res)
    assert widget.loss_1_values["loss"] == [1, 1, 1, 1]
    assert widget.loss_2_values == [1, 1, 1, 1]


def test_unsupervised_training(make_napari_viewer_proxy):
    viewer = make_napari_viewer_proxy()
    widget = Trainer(viewer)
    widget.log = LogFixture()
    widget.worker = None
    widget._toggle_unsupervised_mode(enabled=True)
    widget.model_choice.setCurrentText("WNet")

    widget.patch_choice.setChecked(True)
    [w.setValue(4) for w in widget.patch_size_widgets]

    widget.unsupervised_images_filewidget.text_field.setText(
        str(im_path.parent)
    )
    # widget.start()
    widget.data = widget.create_dataset_dict_no_labs()
    widget.worker = widget._create_worker(
        additional_results_description="wnet_test"
    )
    assert widget.worker.config.train_data_dict is not None
    res = next(
        widget.worker.train(
            provided_model=WNetFixture(),
            provided_optimizer=OptimizerFixture(),
            provided_loss=LossFixture(),
        )
    )
    assert isinstance(res, TrainingReport)
