import sys
import os
import glob
import cv2

EXTENSIONS = {'.mov', '.mp4', '.h264', '.avi'}

CFG_TEMPLATE = """\
x={x}
y={y}
w={w}
h={h}
check_frame=100
blank_0=0
blank_n=590
crop_0=0
crop_n=590
threshold="auto"
diameter=11
minmass=200
maxsize=25
ecc_low=0.05
ecc_high=0.65
vials=1
window=50
pixel_to_cm=1
frame_rate=60
vial_id_vars=5
outlier_TB=1
outlier_LR=3
naming_convention="group_date_condition_fly_id_trial"
file_suffix="MOV"
convert_to_cm_sec=False
trim_outliers=True
fng_smooth_window=5
fng_climb_thresh=0.10
fng_fall_thresh=0.10
fng_min_gap=5
fng_enabled=True
path_project={path_project}
"""

def find_videos(folder):
    videos = []
    for entry in sorted(os.listdir(folder)):
        ext = os.path.splitext(entry)[1].lower()
        if ext in EXTENSIONS:
            videos.append(os.path.join(folder, entry))
    return videos

def get_first_frame(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None
    ret, frame = cap.read()
    cap.release()
    return frame if ret else None

def main():
    if len(sys.argv) != 2:
        print("Usage: python roi_selector.py <folder_path>")
        sys.exit(1)

    folder = sys.argv[1]
    if not os.path.isdir(folder):
        print(f"Error: '{folder}' is not a valid directory.")
        sys.exit(1)

    # Normalise to forward slashes with trailing slash for path_project
    path_project = folder.replace('\\', '/').rstrip('/') + '/'

    videos = find_videos(folder)
    if not videos:
        print("No video files found in the specified folder.")
        sys.exit(0)

    created = 0
    skipped = 0
    escaped = 0

    for video_path in videos:
        stem = os.path.splitext(video_path)[0]
        cfg_path = stem + '.cfg'

        if os.path.exists(cfg_path):
            print(f"[skip]    {os.path.basename(video_path)}  (cfg already exists)")
            skipped += 1
            continue

        frame = get_first_frame(video_path)
        if frame is None:
            print(f"[error]   {os.path.basename(video_path)}  (could not read first frame)")
            escaped += 1
            continue

        title = f"Select ROI — {os.path.basename(video_path)}"
        # fromCenter=False so the rectangle is drawn from the top-left corner
        roi = cv2.selectROI(title, frame, fromCenter=False, printNotice=True)
        cv2.destroyAllWindows()

        x, y, w, h = roi

        # selectROI returns (0,0,0,0) when the user presses Escape
        if w == 0 or h == 0:
            print(f"[escaped] {os.path.basename(video_path)}")
            escaped += 1
            continue

        cfg_content = CFG_TEMPLATE.format(
            x=x, y=y, w=w, h=h,
            path_project=path_project,
        )

        with open(cfg_path, 'w') as f:
            f.write(cfg_content)

        print(f"[created] {os.path.basename(cfg_path)}  (x={x}, y={y}, w={w}, h={h})")
        created += 1

    print()
    print("=== Summary ===")
    print(f"  Created : {created}")
    print(f"  Skipped : {skipped}  (cfg already existed)")
    print(f"  Escaped : {escaped}  (Esc pressed or unreadable)")

if __name__ == '__main__':
    main()
