from pathlib import Path
import sys

from decoder import decode_html


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python test_decoder.py /path/to/input.html")
    source = Path(sys.argv[1]).read_text(encoding="utf-8-sig")
    result = decode_html(source)
    print(f"Decoded layers: {result.layers}")
    for note in result.notes:
        print(note)
    if result.layers == 0:
        raise SystemExit("No supported encoding pattern found.")
    if "<!doctype html>" not in result.text.lower() and "<html" not in result.text.lower():
        raise SystemExit("Output does not look like HTML; refusing to write a result.")
    output = Path("decoded_output.html")
    output.write_text(result.text, encoding="utf-8")
    print(f"Wrote {output.resolve()}")


if __name__ == "__main__":
    main()
      
