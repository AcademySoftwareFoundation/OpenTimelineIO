# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

import os

import opentimelineio as otio
import unreal

from .adapter import import_otio, export_otio


@unreal.uclass()
class OTIOScriptedSequenceImportFactory(unreal.Factory):
    """Adds support for importing OTIO supported file formats to create
    or update level sequence hierarchies via UE import interfaces.
    """

    def _post_init(self, *args):
        self.create_new = False
        self.edit_after_new = True
        self.supported_class = unreal.LevelSequence
        self.editor_import = True
        self.text = False

        # Register all supported timeline import adapters. A comma-separated
        # list of suffixes can be defined by the environment, or all suffixes
        # will be registered.
        env_suffixes = os.getenv("OTIO_UE_IMPORT_SUFFIXES")
        if env_suffixes is not None:
            suffixes = env_suffixes.split(",")
        else:
            suffixes = otio.adapters.suffixes_with_defined_adapters(read=True)
        for suffix in suffixes:
            if suffix.startswith("otio"):
                self.formats.append(suffix + ";OpenTimelineIO files")
            else:
                self.formats.append(suffix + ";OpenTimelineIO supported files")

    @unreal.ufunction(override=True)
    def script_factory_can_import(self, filename):
        suffixes = {
            s.lower() for s in otio.adapters.suffixes_with_defined_adapters(read=True)
        }
        return unreal.Paths.get_extension(filename).lower() in suffixes

    @unreal.ufunction(override=True)
    def script_factory_create_file(self, task):
        # Ok to overwrite an existing level sequence?
        if task.destination_path and task.destination_name:
            asset_path = "{path}/{name}".format(
                path=task.destination_path.replace("\\", "/").rstrip("/"),
                name=task.destination_name,
            )
            level_seq_data = unreal.EditorAssetLibrary.find_asset_data(asset_path)
            if level_seq_data.is_valid() and not task.replace_existing:
                return False

        level_seq, _ = import_otio(
            task.filename,
            destination_path=task.destination_path,
            destination_name=task.destination_name,
        )
        task.result.append(level_seq)
        return True


@unreal.uclass()
class OTIOScriptedSequenceExporter(unreal.Exporter):
    """Adds support for exporting OTIO files from level sequence
    hierarchies via UE export interfaces.
    """

    def _post_init(self, *args):
        # Register one supported timeline export adapter, which can be defined
        # by the environment, or fallback to the default "otio" format.
        suffix = os.getenv("OTIO_UE_EXPORT_SUFFIX", "otio")

        self.format_extension = [suffix]
        self.format_description = ["OpenTimelineIO file"]
        self.supported_class = unreal.LevelSequence
        self.text = False

    @unreal.ufunction(override=True)
    def script_run_asset_export_task(self, task):
        # Ok to overwrite an existing timeline file?
        if not task.replace_identical and unreal.Paths.file_exists(task.filename):
            return False

        export_otio(task.filename, task.object)
        return True
