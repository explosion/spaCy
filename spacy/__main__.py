if __name__ == "__main__":
    import plac
    import sys
    from wasabi import msg
    from spacy.cli import download, link, info, package, train, pretrain, convert
    from spacy.cli import init_model, profile, evaluate, validate, debug_data
    from spacy.cli import train_from_config_cli

    commands = {
        "download": download,
        "link": link,
        "info": info,
        "train": train,
        "train-from-config": train_from_config_cli,
        "pretrain": pretrain,
        "debug-data": debug_data,
        "evaluate": evaluate,
        "convert": convert,
        "package": package,
        "init-model": init_model,
        "profile": profile,
        "validate": validate,
    }
    if len(sys.argv) == 1:
        msg.info("Available commands", ", ".join(commands), exits=1)
    command = sys.argv.pop(1)
    sys.argv[0] = f"spacy {command}"
    if command in commands:
        plac.call(commands[command], sys.argv[1:])
    else:
        available = f"Available: {', '.join(commands)}"
        msg.fail(f"Unknown command: {command}", available, exits=1)
