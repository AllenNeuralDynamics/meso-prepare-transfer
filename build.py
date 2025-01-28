from PyInstaller import __main__ as pyi


def main():
    """Build watchdog service executable using PyInstaller"""
    args = [
        "src/aind_mesoscope_user_schema_ui/main.py",
        "--name",
        "prepare_transfer",
        "--additional-hooks-dir=.",
        "--collect-all",
        "aind_data_schema",
        "--collect-all",
        "aind_data_schema_models",
        "--collect-all",
        "aind_metadata_mapper",
        "--collect-all",
        "scipy",
        # "--noconsole",
        # "--icon",
        # "src/aind_mesoscope_user_schema_ui/icons/prepare.ico",
        "--clean",
    ]
    pyi.run(args)


if __name__ == "__main__":
    main()
