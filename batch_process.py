import sys
import os
import pandas as pd

# ── Hard-coded import path for FreeClimber-FNG detector ──────────────────────
DETECTOR_DIR = r'C:\Users\Vasuj\FreeClimber-FNG-2025\scripts'
if DETECTOR_DIR not in sys.path:
    sys.path.insert(0, DETECTOR_DIR)
from detector import detector

# ── Constants ─────────────────────────────────────────────────────────────────
EXTENSIONS   = {'.mov', '.mp4', '.h264', '.avi'}
MASTER_NAME  = 'master_fng.csv'
META_COLS    = ['group', 'date', 'condition', 'fly_id', 'trial']


def find_videos(folder):
    """Return sorted list of video paths that also have a matching .cfg file."""
    videos, skipped = [], []
    for entry in sorted(os.listdir(folder)):
        ext = os.path.splitext(entry)[1].lower()
        if ext not in EXTENSIONS:
            continue
        video_path = os.path.join(folder, entry)
        cfg_path   = os.path.splitext(video_path)[0] + '.cfg'
        if os.path.exists(cfg_path):
            videos.append(video_path)
        else:
            skipped.append(entry)
    return videos, skipped


def parse_stem(video_path):
    """Split filename stem on '_' and return the first five fields."""
    stem   = os.path.splitext(os.path.basename(video_path))[0]
    parts  = stem.split('_')
    padded = (parts + [''] * 5)[:5]   # pad if fewer than 5 parts
    return dict(zip(META_COLS, padded))


def run_pipeline(video_path):
    """Initialise detector and run steps 1–7. Returns the detector object."""
    cfg_path = os.path.splitext(video_path)[0] + '.cfg'
    d = detector(video_path, config_file=cfg_path)
    d.step_1()
    d.step_2()
    d.step_3()
    d.step_4()
    d.step_5()   # writes .fng.csv
    d.step_6()
    d.step_7()
    return d


def load_fng(video_path):
    """Read the .fng.csv written next to the video by step_5."""
    fng_path = '.'.join(video_path.split('.')[:-1]) + '.fng.csv'
    if not os.path.exists(fng_path):
        raise FileNotFoundError(f'.fng.csv not found at: {fng_path}')
    return pd.read_csv(fng_path)


def prepend_meta(df, meta):
    """Insert metadata columns at the front of the dataframe."""
    for col in reversed(META_COLS):
        df.insert(0, col, meta[col])
    return df


def save_master(df, output_folder):
    """Append df to master_fng.csv (or create it) in output_folder."""
    os.makedirs(output_folder, exist_ok=True)
    master_path = os.path.join(output_folder, MASTER_NAME)
    if os.path.exists(master_path):
        existing = pd.read_csv(master_path)
        df = pd.concat([existing, df], ignore_index=True)
    df.to_csv(master_path, index=False)
    return master_path


def main():
    if len(sys.argv) != 3:
        print('Usage: python batch_process.py <input_folder> <output_folder>')
        sys.exit(1)

    input_folder  = sys.argv[1]
    output_folder = sys.argv[2]

    if not os.path.isdir(input_folder):
        print(f"Error: input folder '{input_folder}' does not exist.")
        sys.exit(1)

    videos, skipped_no_cfg = find_videos(input_folder)

    if not videos and not skipped_no_cfg:
        print('No video files found in the input folder.')
        sys.exit(0)

    if not videos:
        print('No videos with matching .cfg files found. Nothing to process.')
        print_summary(0, 0, [], skipped_no_cfg, None)
        sys.exit(0)

    master_frames = []
    succeeded     = 0
    failed        = []   # list of (filename, error_message)

    for video_path in videos:
        name = os.path.basename(video_path)
        print(f'\n{"="*60}')
        print(f'Processing: {name}')
        print(f'{"="*60}')
        try:
            run_pipeline(video_path)
            df   = load_fng(video_path)
            meta = parse_stem(video_path)
            df   = prepend_meta(df, meta)
            master_frames.append(df)
            succeeded += 1
            print(f'  -> Done: {len(df)} FNG event(s) detected.')
        except BaseException as exc:
            msg = f'{type(exc).__name__}: {exc}'
            failed.append((name, msg))
            print(f'  !! FAILED: {msg}')

    # Save master CSV if there is anything to save
    master_path = None
    if master_frames:
        combined    = pd.concat(master_frames, ignore_index=True)
        master_path = save_master(combined, output_folder)

    print_summary(len(videos), succeeded, failed, skipped_no_cfg, master_path)


def print_summary(total, succeeded, failed, skipped_no_cfg, master_path):
    width = 60
    print(f'\n{"="*width}')
    print('BATCH SUMMARY')
    print(f'{"="*width}')
    print(f'  Videos found          : {total}')
    print(f'  Succeeded             : {succeeded}')
    print(f'  Failed                : {len(failed)}')
    print(f'  Skipped (no .cfg)     : {len(skipped_no_cfg)}')

    if failed:
        print('\n  Failed videos:')
        for fname, msg in failed:
            print(f'    - {fname}')
            print(f'      {msg}')

    if skipped_no_cfg:
        print('\n  Skipped (no .cfg):')
        for fname in skipped_no_cfg:
            print(f'    - {fname}')

    if master_path:
        print(f'\n  Master CSV: {master_path}')
    else:
        print('\n  Master CSV: not written (no successful runs)')
    print(f'{"="*width}')


if __name__ == '__main__':
    main()
