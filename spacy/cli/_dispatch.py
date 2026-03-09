from typing import Dict, Iterable, Optional, Tuple


CommandPath = Tuple[str, ...]


TOP_LEVEL_MODULES: Dict[str, Tuple[str, ...]] = {
    "apply": ("spacy.cli.apply",),
    "assemble": ("spacy.cli.assemble",),
    "convert": ("spacy.cli.convert",),
    "debug-data": ("spacy.cli.debug_data",),
    "download": ("spacy.cli.download",),
    "evaluate": ("spacy.cli.evaluate",),
    "find-function": ("spacy.cli.find_function",),
    "find-threshold": ("spacy.cli.find_threshold",),
    "info": ("spacy.cli.info",),
    "package": ("spacy.cli.package",),
    "pretrain": ("spacy.cli.pretrain",),
    "profile": ("spacy.cli.profile",),
    "train": ("spacy.cli.train",),
    "validate": ("spacy.cli.validate",),
}


GROUP_MODULES: Dict[str, Tuple[str, ...]] = {
    "benchmark": (
        "spacy.cli.benchmark_speed",
        "spacy.cli.evaluate",
    ),
    "debug": (
        "spacy.cli.debug_config",
        "spacy.cli.debug_data",
        "spacy.cli.debug_diff",
        "spacy.cli.debug_model",
        "spacy.cli.profile",
    ),
    "init": (
        "spacy.cli.init_config",
        "spacy.cli.init_pipeline",
    ),
}


SUBCOMMAND_MODULES: Dict[CommandPath, Tuple[str, ...]] = {
    ("benchmark", "accuracy"): ("spacy.cli.evaluate",),
    ("benchmark", "speed"): ("spacy.cli.benchmark_speed",),
    ("debug", "config"): ("spacy.cli.debug_config",),
    ("debug", "data"): ("spacy.cli.debug_data",),
    ("debug", "diff-config"): ("spacy.cli.debug_diff",),
    ("debug", "model"): ("spacy.cli.debug_model",),
    ("debug", "profile"): ("spacy.cli.profile",),
    ("init", "config"): ("spacy.cli.init_config",),
    ("init", "fill-config"): ("spacy.cli.init_config",),
    ("init", "labels"): ("spacy.cli.init_pipeline",),
    ("init", "nlp"): ("spacy.cli.init_pipeline",),
    ("init", "vectors"): ("spacy.cli.init_pipeline",),
}


PUBLIC_ATTRS: Dict[str, Tuple[str, Optional[str]]] = {
    "app": ("spacy.cli._util", "app"),
    "apply": ("spacy.cli.apply", "apply"),
    "assemble_cli": ("spacy.cli.assemble", "assemble_cli"),
    "benchmark_speed_cli": ("spacy.cli.benchmark_speed", "benchmark_speed_cli"),
    "convert": ("spacy.cli.convert", "convert"),
    "debug_config": ("spacy.cli.debug_config", "debug_config"),
    "debug_data": ("spacy.cli.debug_data", "debug_data"),
    "debug_diff": ("spacy.cli.debug_diff", "debug_diff"),
    "debug_model": ("spacy.cli.debug_model", "debug_model"),
    "download": ("spacy.cli.download", "download"),
    "download_module": ("spacy.cli.download", None),
    "evaluate": ("spacy.cli.evaluate", "evaluate"),
    "fill_config": ("spacy.cli.init_config", "fill_config"),
    "find_function": ("spacy.cli.find_function", "find_function"),
    "find_threshold": ("spacy.cli.find_threshold", "find_threshold"),
    "info": ("spacy.cli.info", "info"),
    "init_config": ("spacy.cli.init_config", "init_config"),
    "init_pipeline_cli": ("spacy.cli.init_pipeline", "init_pipeline_cli"),
    "package": ("spacy.cli.package", "package"),
    "pretrain": ("spacy.cli.pretrain", "pretrain"),
    "profile": ("spacy.cli.profile", "profile"),
    "project_assets": ("spacy.cli.project.assets", "project_assets"),
    "project_clone": ("spacy.cli.project.clone", "project_clone"),
    "project_document": ("spacy.cli.project.document", "project_document"),
    "project_pull": ("spacy.cli.project.pull", "project_pull"),
    "project_push": ("spacy.cli.project.push", "project_push"),
    "project_run": ("spacy.cli.project.run", "project_run"),
    "project_update_dvc": ("spacy.cli.project.dvc", "project_update_dvc"),
    "train_cli": ("spacy.cli.train", "train_cli"),
    "validate": ("spacy.cli.validate", "validate"),
}


def iter_builtin_modules() -> Iterable[str]:
    seen = set()
    for modules in TOP_LEVEL_MODULES.values():
        for module in modules:
            if module not in seen:
                seen.add(module)
                yield module
    for modules in GROUP_MODULES.values():
        for module in modules:
            if module not in seen:
                seen.add(module)
                yield module
