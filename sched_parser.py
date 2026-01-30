'''
Code Purpose: Parse sched.txt files and extract metadata
Author: Owen A. Johnson
'''
from glob import glob
from datetime import datetime
import re
import pandas as pd


def parse_schedule(text: str, sched_file: str):
    rows = []

    line_re = re.compile(
        r"^\s*(?P<start>\d{4}-\d{2}-\d{2}T\d{2}:\d{2})\s*-\s*"
        r"(?P<end>\d{4}-\d{2}-\d{2}T\d{2}:\d{2})\s*:\s*"
        r"(?P<rest>.+?)\s*$"
    )
    bracket_re = re.compile(r"\[(.*?)\]")

    for raw in text.splitlines():
        line = raw.strip()
        if not line or "#" in line:
            continue

        m = line_re.match(line)
        if not m:
            continue

        start = m.group("start")
        end = m.group("end")
        rest = m.group("rest").strip()

        # duration
        t0 = datetime.fromisoformat(start)
        t1 = datetime.fromisoformat(end)
        duration_s = (t1 - t0).total_seconds()
        duration_min = duration_s / 60.0

        # Find all bracket blocks and use the LAST one as "metadata"
        blocks = list(bracket_re.finditer(rest))
        meta_inside = None
        source_part = rest

        if blocks:
            last = blocks[-1]
            meta_inside = last.group(1).strip()
            # remove ONLY the last [...] from the end/source string
            source_part = (rest[: last.start()] + rest[last.end():]).strip()

        # Clean source name: strip stray brackets/spaces
        source_clean = source_part.strip().strip("[]").strip()

        # If the "meta" block is Sun357 OR the source itself is Sun357
        if (source_clean.lower() == "sun357") or (meta_inside and meta_inside.strip().lower() == "sun357"):
            rows.append({
                "sched_file": sched_file,
                "start": start,
                "end": end,
                "duration_s": duration_s,
                "duration_min": duration_min,
                "source": "Sun357",
                "ra_rad": None,
                "dec_rad": None,
                "frame": None,
            })
            continue

        ra = dec = frame = None

        if meta_inside:
            # Try to parse coords from last bracket block
            parts = [p.strip() for p in meta_inside.split(",")]
            # Require first 2 fields to be float-like; otherwise treat as "no coords"
            try:
                if len(parts) >= 2:
                    ra = float(parts[0])
                    dec = float(parts[1])
                if len(parts) >= 3:
                    frame = parts[2].strip().strip("'\"")
            except ValueError:
                ra = dec = frame = None

        rows.append({
            "sched_file": sched_file,
            "start": start,
            "end": end,
            "duration_s": duration_s,
            "duration_min": duration_min,
            "source": source_clean,
            "ra_rad": ra,
            "dec_rad": dec,
            "frame": frame,
        })

    return rows


def main():
    # sched_files = glob('/home/ilofar/scheduling/archive/old_sched/sched*.txt')
    sched_files = glob('./sched_archive/sched*.txt')

    rows = []
    for sf in sorted(sched_files):
        print('ye')
        try:
            with open(sf, "r") as f:
                text = f.read()
            rows.extend(parse_schedule(text, sf))
        except (OSError, UnicodeDecodeError) as e:
            # keep going; record file-level error row
            rows.append({
                "sched_file": sf,
                "start": None,
                "end": None,
                "source": None,
                "ra_rad": None,
                "dec_rad": None,
                "frame": None,
                "error": str(e),
            })

    df = pd.DataFrame(rows)
    df.to_csv("REALTA-Sched-Metadata.csv", index=False)


if __name__ == "__main__":
    main()
