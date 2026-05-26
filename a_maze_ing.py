from parser import MazeConfig


if __name__ == "__main__":
    config = MazeConfig()
    config.parse_config()
    print(
        f"WIDTH={config.width}\n"
        f"HEIGHT={config.height}\n"
        f"ENTRY={config.entry}\n"
        f"EXIT={config.exit_}\n"
        f"OUTPUT_FILE={config.output_file}\n"
        f"PERFECT={config.perfect}\n"
        f"SEED={config.seed}"
        )
