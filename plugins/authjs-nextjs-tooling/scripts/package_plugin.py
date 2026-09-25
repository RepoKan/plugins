import argparse
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
INCLUDED = (
    "plugin.json",
    ".app.json",
    ".codex-plugin",
    "README.md",
    "references",
    "skills",
)


def iter_files():
    for name in INCLUDED:
        path = PLUGIN_ROOT / name
        paths = (
            [path]
            if path.is_file()
            else sorted(item for item in path.rglob("*") if item.is_file())
        )
        for item in paths:
            if item.is_symlink():
                raise ValueError(f"symlink is not allowed: {item}")
            yield item


def build(output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w", compression=ZIP_DEFLATED) as archive:
        for path in iter_files():
            relative = path.relative_to(PLUGIN_ROOT)
            info = ZipInfo(
                f"{PLUGIN_ROOT.name}/{relative.as_posix()}",
                date_time=(1980, 1, 1, 0, 0, 0),
            )
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    build(parser.parse_args().output.resolve())
