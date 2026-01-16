"""Module to create a dummy mesoscope dataset"""

import json
from pathlib import Path


def acquisition_data_files(session_id: str, parent_session_ids: list[str]) -> list:
    """List of files and folders matching mesoscope acquisition data structure"""
    files = [
        f"{session_id}.html",
        f"{session_id}_averaged_depth.tiff",
        f"{session_id}_averaged_surface.tiff",
        f"{session_id}_local_z_stack0.tiff",
        f"{session_id}_local_z_stack1.tiff",
        f"{session_id}_local_z_stack2.tiff",
        f"{session_id}_local_z_stack3.tiff",
        f"{session_id}_platform.json",
        f"{session_id}_reticle.tif",
        f"{session_id}_stim.pkl",
        f"{session_id}_stim_table.csv",
        f"{session_id}_surface.roi",
        f"{session_id}_sync.h5",
        f"{session_id}_timeseries.roi",
        f"{session_id}_timeseries.tiff",
        f"{session_id}_timeseries_Motion_00001.csv",
        f"{session_id}_timeseries_Motion_Corrected_00001.csv",
        f"{session_id}_timeseries_Motion_Estimator_Descriptor_00001.csv",
        f"{session_id}_vasculature.tif",
        f"{session_id}_vsync_table.csv",
        "data_description.json",
        "lightleak_average.tiff",
        "light_leak_test_00001.tif",
        "session",
        "session.json",
        {
            "depth_2p_images": [
                f"{session_id}_-114.tif",
                f"{session_id}_-152.tif",
                f"{session_id}_-205.tif",
                f"{session_id}_-248.tif",
                f"{session_id}_-285.tif",
                f"{session_id}_-29.tif",
                f"{session_id}_-327.tif",
                f"{session_id}_-69.tif",
            ]
        },
        {"parent_session_depth_images": [f"{parent_id}_depth.tif" for parent_id in parent_session_ids]},
        {"parent_session_surface_images": [f"{parent_id}_surface.tif" for parent_id in parent_session_ids]},
        {
            "sessions": [
                "session_beam_mapping_corrected.pkl",
                "session_cortical_stack_check.pkl",
                "session_depth_2p_image_acquisition.pkl",
                "session_depth_2p_image_approve.pkl",
                "session_depth_2p_setup.pkl",
                "session_finalize.pkl",
                "session_focus_vasculature.pkl",
                "session_full_field_check.pkl",
                "session_light_leak_review.pkl",
                "session_light_leak_test.pkl",
                "session_light_leak_wait.pkl",
                "session_move_to_load_mouse.pkl",
                "session_move_to_measure_mouse.pkl",
                "session_set_up_roi.pkl",
                "session_surface_2p_image_acquisition.pkl",
                "session_surface_2p_image_approve.pkl",
                "session_target_cells_correct_beam_depth.pkl",
                "session_time_series_setup.pkl",
                "session_time_series_setup_state.pkl",
                "session_time_series_wait.pkl",
                "session_two_photon_setup.pkl",
                "session_vasculature_image_acquisition.pkl",
                "session_vasculature_image_approve.pkl",
            ]
        },
        {
            "sorted_local_z_stacks": [
                f"{session_id}_local_z_stack0_reg_ch_1.tif",
                f"{session_id}_local_z_stack0_reg_ch_2.tif",
                f"{session_id}_local_z_stack1_reg_ch_1.tif",
                f"{session_id}_local_z_stack1_reg_ch_2.tif",
                f"{session_id}_local_z_stack2_reg_ch_1.tif",
                f"{session_id}_local_z_stack2_reg_ch_2.tif",
                f"{session_id}_local_z_stack3_reg_ch_1.tif",
                f"{session_id}_local_z_stack3_reg_ch_2.tif",
            ]
        },
        {
            "surface_2p_images": [
                f"{session_id}_-355.tif",
            ]
        },
    ]

    return files


def behavior_data_files(session_id: str) -> list:
    """List of behavior video files matching mesoscope structure"""
    return [
        f"{session_id}_Behavior_20250615T120000.mp4",
        f"{session_id}_Face_20250615T120000.mp4",
        f"{session_id}_Eye_20250615T120000.mp4",
        f"{session_id}_Nose_20250615T120000.mp4",
        f"{session_id}_Behavior_20250615T120000.json",
        f"{session_id}_Face_20250615T120000.json",
        f"{session_id}_Eye_20250615T120000.json",
        f"{session_id}_Nose_20250615T120000.json",
    ]


def _create_empty_files(parent_dir: Path, items: list[str | dict]):
    """Create files and folders from a list where strings -> files and dicts -> subdirectories"""
    parent_dir.mkdir(parents=True, exist_ok=True)
    for item in items:
        if isinstance(item, dict):
            # It's a subdirectory
            for folder_name, contents in item.items():
                subfolder = parent_dir / folder_name
                _create_empty_files(subfolder, contents)
        else:
            # It's a file
            (parent_dir / item).touch()


def make_dummy_dataset(
    acquisition_dir: Path,
    behavior_video_dir: Path,
    subject_id: str,
    project_code: str,
    session_id: str,
):
    """Create a dummy dataset for testing purposes matching real mesoscope structure"""

    # Make some parent session ids as well
    parent_session_ids = [str(int(session_id) - 1000000 + i) for i in range(9)]

    # Create dummy acquisition data
    acquisition_data = acquisition_data_files(session_id, parent_session_ids)
    _create_empty_files(acquisition_dir / session_id, acquisition_data)

    # Create platform.json with actual data
    platform_data = {"subject_id": subject_id, "project_code": project_code}
    platform_json_path = acquisition_dir / session_id / f"{session_id}_platform.json"
    platform_json_path.write_text(json.dumps(platform_data))

    # Create dummy behavior video data
    behavior_video_structure = behavior_data_files(session_id)
    _create_empty_files(behavior_video_dir, behavior_video_structure)

    # Also create video files for other sessions to be ignored
    for session in parent_session_ids:
        behavior_data = behavior_data_files(session)
        _create_empty_files(behavior_video_dir, behavior_data)
