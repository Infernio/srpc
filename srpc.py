#!/usr/bin/python3

#  srpc - Search and Replace while Preserving Case
#  Copyright (C) 2026 Infernio
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import argparse
import re
import traceback
from itertools import zip_longest
from pathlib import Path

def main() -> None:
    run(parse_args())

class SrpcArgs(argparse.Namespace):
    target: str
    replacement: str
    files: list[str]
    dry_run: bool
    verbose: bool

def parse_args() -> SrpcArgs:
    parser = argparse.ArgumentParser(
        prog='srpc',
        description='Search and Replace while Preserving Case',
    )
    parser.add_argument('target', help='The string to replace')
    parser.add_argument('replacement', help='The string to replace the target with')
    parser.add_argument('files', nargs='+', help='The files in which to perform the replacement')
    parser.add_argument('-d', '--dry-run', action='store_true', help='If set, do not perform any writes')
    parser.add_argument('-v', '--verbose', action='store_true', help='If set, log how many replacements were performed '
                                                                     'in each file')
    return parser.parse_args(namespace=SrpcArgs())

def run(args: SrpcArgs) -> None:
    files = [Path(f) for f in args.files]
    for f in files:
        try:
            with f.open() as ins:
                lines = ins.readlines()
        except OSError:
            traceback.print_exc()
            exit(1)
        new_lines = replace(f, lines, args)
        write(f, new_lines, args)

def replace(path: Path, lines: list[str], args: SrpcArgs) -> list[str]:
    new_lines = []
    target_regex = re.compile(re.escape(args.target), re.I)
    num_replaced = 0
    for line in lines:
        matches = list(target_regex.finditer(line))
        if matches:
            num_replaced += len(matches)
            processed_matches = process_matches(matches, args)
            remaining_parts = target_regex.split(line)
            new_lines.append(recombine_line(processed_matches, remaining_parts))
        else:
            # No match on this line, keep unchanged
            new_lines.append(line)
    if args.verbose:
        print(f'Replaced {num_replaced} occurrence(s) in {path}')
    return new_lines

def process_matches(matches: list[re.Match[str]], args: SrpcArgs) -> list[str]:
    new_matches = []
    for match in matches:
        new_text = []
        for cs, ct in zip_longest(list(match.group()), list(args.replacement)):
            if ct is None:
                # We've reached the end of the replacement, thus we're done
                break
            if cs is not None:
                # We still have letters in the source, so copy the case from there
                ct = ct.upper() if cs.isupper() else ct.lower()
            new_text.append(ct)
        new_matches.append(''.join(new_text))
    return new_matches

def recombine_line(processed_matches: list[str], remaining_parts: list[str]) -> str:
    line = []
    for i, part in enumerate(remaining_parts):
        # We always start with a split part. Even if the string begins with the pattern, we will still get an empty
        # string from the split call.
        line.append(part)
        # For the last part, there is no following match. The number of parts will always be the number of matches + 1.
        if i < len(processed_matches):
            line.append(processed_matches[i])
    return ''.join(line)

def write(path: Path, lines: list[str], args: SrpcArgs):
    if args.dry_run:
        return
    with path.open('w') as out:
        out.write(''.join(lines))

if __name__ == '__main__':
    main()
