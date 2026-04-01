!/usr/bin/env python3

import argparse
import sys

def full_percent_encode(text: str) -> str:
    """
    Fully percent-encode a string.
    Every UTF-8 byte becomes %HH (uppercase hex).
    """
    return "".join(f"%{b:02X}" for b in text.encode("utf-8"))

def interactive_loop():
    print("Full Percent Encoder (interactive mode)")
    print("Press Ctrl+C or Ctrl+D to exit\n")

    while True:
        try:
            user_input = input('Input: ')
            if user_input == "":
                print("Output: ")
                continue

            encoded = full_percent_encode(user_input)
            print(f"Output: {encoded}\n")

        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

def main():
    parser = argparse.ArgumentParser(
        description="Fully percent-encode all characters (byte-level UTF-8)."
    )
    parser.add_argument(
        "--input",
        help="Input string to percent-encode (one-time mode)"
    )

    args = parser.parse_args()

    if args.input is not None:
        # One-time mode
        try:
            print(full_percent_encode(args.input))
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Interactive mode
        interactive_loop()

if __name__ == "__main__":
    main()
