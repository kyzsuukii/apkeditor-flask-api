# -*- coding: utf-8 -*-

"""

Copyright (c) 2024 Dwiky Rizky Ananditya

All rights reserved.


This code is licensed under the MIT License.

You may obtain a copy of the License at

https://opensource.org/licenses/MIT

"""

from dataclasses import dataclass
import os
from typing import Any, Dict, List, Optional

from app.lib.shell import Shell


@dataclass
class BaseOptions:
    f: bool = False
    vrd: bool = False


@dataclass
class DecodeOptions(BaseOptions):
    framework: Optional[List[str]] = None
    framework_version: Optional[str] = None
    res_dir: Optional[str] = None
    sig: Optional[str] = None
    t: Optional[str] = None
    dex: bool = False
    dex_markers: bool = False
    keep_res_path: bool = False
    no_dex_debug: bool = False
    split_json: bool = False


@dataclass
class RefactorOptions(BaseOptions):
    public_xml: Optional[str] = None
    clean_meta: bool = False
    fix_types: bool = False


@dataclass
class BuildOptions(BaseOptions):
    framework: Optional[List[str]] = None
    framework_version: Optional[str] = None
    res_dir: Optional[str] = None
    sig: Optional[str] = None
    t: Optional[str] = None
    no_cache: bool = False


@dataclass
class MergeOptions(BaseOptions):
    res_dir: Optional[str] = None
    clean_meta: bool = False
    validate_modules: bool = False


@dataclass
class ProtectOptions(BaseOptions):
    keep_type: Optional[List[str]] = None
    skip_manifest: bool = False


class ApkEditorOptions:
    DECODE = "decode"
    REFACTOR = "refactor"
    BUILD = "build"
    MERGE = "merge"
    PROTECT = "protect"


class ApkEditor:
    def __init__(self, apk_editor_path: str):
        self.java_jar = Shell("java -jar")
        self.apk_editor = apk_editor_path
        if not os.path.isfile(self.apk_editor):
            raise RuntimeError("APK editor not found")

    def _build_args(
        self,
        command: str,
        apk_path: str,
        output_path: Optional[str] = None,
        options: Dict[str, Any] = None,
    ) -> List[str]:
        args = [self.apk_editor, command, "-i", apk_path]
        if output_path:
            args.extend(["-o", output_path])
        if options:
            for key, value in options.items():
                if isinstance(value, bool):
                    if value:
                        args.append(f"-{key.replace('_', '-')}")
                elif value is not None:
                    if isinstance(value, list):
                        args.extend([f"-{key.replace('_', '-')}", ",".join(value)])
                    else:
                        args.extend([f"-{key.replace('_', '-')}", str(value)])
        return args

    def _execute(
        self,
        command: str,
        apk_path: str,
        output_path: Optional[str] = None,
        options: Any = None,
    ) -> str:
        options_dict = vars(options) if options else {}
        args = self._build_args(command, apk_path, output_path, options_dict)
        self.java_jar.add_template(command, args)
        self.java_jar.use_template(command)
        self.java_jar.run()
        if self.java_jar.fail():
            raise RuntimeError(f"Failed to {command} APK: {self.java_jar.error()}")
        return output_path or apk_path

    def run(
        self,
        command: str,
        apk_path: str,
        output_path: Optional[str] = None,
        options: Any = None,
    ) -> str:
        return self._execute(command, apk_path, output_path, options)

    def decode(
        self,
        apk_path: str,
        output_path: Optional[str] = None,
        options: DecodeOptions = None,
    ) -> str:
        return self.run(ApkEditorOptions.DECODE, apk_path, output_path, options)

    def refactor(
        self,
        apk_path: str,
        output_path: Optional[str] = None,
        options: RefactorOptions = None,
    ) -> str:
        return self.run(ApkEditorOptions.REFACTOR, apk_path, output_path, options)

    def build(
        self,
        apk_path: str,
        output_path: Optional[str] = None,
        options: BuildOptions = None,
    ) -> str:
        return self.run(ApkEditorOptions.BUILD, apk_path, output_path, options)

    def merge(
        self,
        apk_path: str,
        output_path: Optional[str] = None,
        options: MergeOptions = None,
    ) -> str:
        return self.run(ApkEditorOptions.MERGE, apk_path, output_path, options)

    def protect(
        self,
        apk_path: str,
        output_path: Optional[str] = None,
        options: ProtectOptions = None,
    ) -> str:
        return self.run(ApkEditorOptions.PROTECT, apk_path, output_path, options)
