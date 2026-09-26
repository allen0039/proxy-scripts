"""Bundle the licensed OpenCC dictionary with the Surge subtitle handler."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / "vendor/opencc-js-1.4.2/t2cn.js"
HANDLER = ROOT / "tools/bilibili_cc_handler.js"
OUTPUT = ROOT / "Scripts/Common/BilibiliCC.js"


def main() -> None:
    banner = (
        "// Bilibili Traditional CC subtitles -> Simplified Chinese.\n"
        "// OpenCC 1.4.2: MIT AND Apache-2.0. See vendor/opencc-js-1.4.2/.\n"
        "// Based on the rule by ddgksf2013; response handling is maintained here.\n"
    )
    OUTPUT.write_text(
        banner + LIBRARY.read_text(encoding="utf-8") + "\n"
        + HANDLER.read_text(encoding="utf-8"),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
