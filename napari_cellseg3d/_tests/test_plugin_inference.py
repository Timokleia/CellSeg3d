from pathlib import Path

from numpy.random import PCG64, Generator
from tifffile import imread

from napari_cellseg3d._tests.fixtures import LogFixture
from napari_cellseg3d.code_models.instance_segmentation import (
    INSTANCE_SEGMENTATION_METHOD_LIST,
    volume_stats,
)
from napari_cellseg3d.code_models.models.model_test import TestModel
from napari_cellseg3d.code_plugins.plugin_model_inference import (
    InferenceResult,
    Inferer,
)
from napari_cellseg3d.config import MODEL_LIST

rand_gen = Generator(PCG64(12345))


def test_inference(make_napari_viewer_proxy, qtbot):
    im_path = str(Path(__file__).resolve().parent / "res/test.tif")
    image = imread(im_path)

    assert image.shape == (6, 6, 6)

    viewer = make_napari_viewer_proxy()
    widget = Inferer(viewer)
    widget.log = LogFixture()
    viewer.window.add_dock_widget(widget)
    viewer.add_image(image)

    assert len(viewer.layers) == 1

    widget.window_infer_box.setChecked(True)
    widget.window_overlap_slider.setValue(0)
    widget.keep_data_on_cpu_box.setChecked(True)

    assert widget.check_ready()

    widget.model_choice.setCurrentText("WNet")
    widget._restrict_window_size_for_model()
    assert widget.window_infer_box.isChecked()
    assert widget.window_size_choice.currentText() == "64"

    test_model_name = "test"
    MODEL_LIST[test_model_name] = TestModel
    widget.model_choice.addItem(test_model_name)
    widget.model_choice.setCurrentText(test_model_name)

    widget.worker_config = widget._set_worker_config()
    assert widget.worker_config is not None
    assert widget.model_info is not None
    widget.window_infer_box.setChecked(False)

    worker = widget._create_worker_from_config(widget.worker_config)
    assert worker.config is not None
    assert worker.config.model_info is not None
    worker.config.layer = viewer.layers[0].data
    worker.config.post_process_config.instance.enabled = True
    worker.config.post_process_config.instance.method = (
        INSTANCE_SEGMENTATION_METHOD_LIST["Watershed"]()
    )

    assert worker.config.layer is not None
    worker.log_parameters()

    res = next(worker.inference())
    assert isinstance(res, InferenceResult)
    assert res.result.shape == (8, 8, 8)
    assert res.instance_labels.shape == (8, 8, 8)
    widget.on_yield(res)

    mock_image = rand_gen.random(size=(10, 10, 10))
    mock_labels = rand_gen.integers(0, 10, (10, 10, 10))
    mock_results = InferenceResult(
        image_id=0,
        original=mock_image,
        instance_labels=mock_labels,
        crf_results=mock_image,
        stats=[volume_stats(mock_labels)],
        result=mock_image,
        model_name="test",
    )
    num_layers = len(viewer.layers)
    widget.worker_config.post_process_config.instance.enabled = True
    widget._display_results(mock_results)
    assert len(viewer.layers) == num_layers + 4

    # assert widget.check_ready()
    # widget._setup_worker()
    # # widget.config.show_results = True
    # with qtbot.waitSignal(widget.worker.yielded, timeout=10000) as blocker:
    #     blocker.connect(
    #         widget.worker.errored
    #     )  # Can add other signals to blocker
    #     widget.worker.start()

    assert widget.on_finish()
