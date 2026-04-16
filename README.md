# FreeClimber-FNG Lab Manual

A start-to-finish protocol for recording, processing, and analyzing *Drosophila melanogaster* negative geotaxis videos using FreeClimber-FNG.

This manual is written for lab members with limited Python experience. Follow each section in order. If something doesn't work, re-read the section before asking for help — most problems come from skipped steps.

---

## 1. Overview

The pipeline has five stages. You will:

1. Record videos of single flies in vials performing a climbing assay.
2. Trim each video to remove pre-trial and post-trial footage.
3. Select the region of interest (ROI) for each video using a GUI tool.
4. Batch-process every video through FreeClimber-FNG.
5. Collect a single master CSV containing all fly/trial data for analysis.

Expect each fly to produce three video files (three trials per fly). A typical experiment of 60 flies yields 180 videos.

---

## 2. What you need before starting

### Hardware

A smartphone or camera capable of recording video at 1920×1080 resolution and 60 frames per second. The specific model does not matter. A flexible phone tripod. Standard *Drosophila* vials (narrow polystyrene, empty). A flat white surface to use as a backdrop (a sheet of printer paper taped to a box works).

### Software

Install the following on the computer that will process the videos:

- **Anaconda** (Python distribution) — https://www.anaconda.com/download
- **Git** — https://git-scm.com/downloads
- **FFmpeg** — https://ffmpeg.org/download.html (add to system PATH during installation)
- **LosslessCut** (video trimming) — https://mifi.no/losslesscut/
- **VS Code** (optional but recommended) — https://code.visualstudio.com/

You do not need Claude Code, Claude, or any AI tool to use this pipeline. Those are optional conveniences, not requirements.

### Repositories

You will clone two GitHub repositories:

1. `FreeClimber-FNG` — the core analysis tool.
2. `FreeClimber-FNG-batch` — two helper scripts (ROI selector and batch processor).

Cloning instructions are in Section 7.

---

## 3. Camera setup

Mount the phone or camera on the tripod so it is level with the vials and pointed horizontally. Position the camera so that the vials fill the entire frame vertically — the bottom of the vial should be near the bottom of the frame, and the top of the vial near the top. Any empty space wastes resolution.

Place the white backdrop behind the vials. The backdrop must be uniform, clean, and free of shadows or markings. Good contrast between the fly (dark) and the background (white) is what makes tracking work.

Lighting should be bright, diffuse, and consistent across trials. Avoid direct sunlight or lamps that cast visible shadows on the backdrop. Fluorescent overhead lighting in most labs is sufficient.

Before every recording session, check that the video settings on the phone are set to **1920×1080 at 60 fps**. Not 30 fps, not 4K, not slow-motion. 1080p60 is the standard.

---

## 4. Assay protocol

### Preparing flies

Use single flies per vial. Transfer one fly into an empty *Drosophila* vial and plug it. Label the vial with the fly's ID number. Let the fly acclimate for at least 30 minutes at room temperature before recording.

### Recording a trial

Place the labeled vial upright in front of the camera with the white backdrop behind it. Start the video recording. Lift the vial a few centimeters off the surface and perform three light, firm taps downward onto the benchtop — this knocks the fly to the bottom of the vial and triggers the negative geotaxis response.

Record for a full 60 seconds from the moment you start recording. Stop the recording.

### Between trials

Rest the fly for 30 seconds between trials. Perform three trials per fly. After the third trial, return the fly to its home vial or proceed to the next fly per your experimental protocol.

### File naming

Videos must be named according to the following convention, separated by underscores:

```
group_date_condition_flyid_trial.MOV
```

Where:
- `group` is the experimental cohort number (e.g., `1`, `2`, `3`)
- `date` is the recording date in MMDDYY format (e.g., `040426` for April 4, 2026)
- `condition` is the treatment condition (e.g., `control`, `etoh`, `tbi`)
- `flyid` is the fly's unique ID number (e.g., `407`)
- `trial` is the trial number (`1`, `2`, or `3`)

Example: `1_040426_etoh_407_1.MOV` is group 1, recorded April 4 2026, etoh condition, fly 407, trial 1.

Rename files immediately after recording. If filenames do not follow this convention, the batch processor will fail.

### Advanced: five-vial videos

You may record up to five vials simultaneously in a single video for efficiency. This requires a different filename convention and additional processing steps that are not covered in this manual.

---

## 5. Trimming videos

Raw videos contain camera movement before the tap-down (setting up, pressing record) and irrelevant footage after the fly has stopped climbing. Both must be removed.

Open LosslessCut. Drag the video file into the window. Scrub through the video and find the **first frame after the final tap**, where the vial has come to rest on the surface and is no longer moving. Set this as the start point (press `I` or click the left bracket icon).

Find the end of the trial — typically around 30-45 seconds after the tap — where the fly has either completed its climbing response or the trial has clearly ended. Set this as the end point (press `O` or click the right bracket icon).

Export the trimmed clip. In LosslessCut's export settings, make sure "Keep all tracks" is selected and the output format matches the input. Save the trimmed video with the **same filename as the original** (LosslessCut by default appends suffixes — disable this in export settings or rename after export).

Place all trimmed videos for a given experimental group into a single folder. Folder naming should match the group identity (e.g., `1_040426_etoh`).

---

## 6. Organizing your folders

Before processing, your file structure should look like this:

```
D:\project_freeclimber\
├── data\
│   ├── video_data\
│   │   ├── 1_040426_etoh\
│   │   │   ├── 1_040426_etoh_407_1.MOV
│   │   │   ├── 1_040426_etoh_407_2.MOV
│   │   │   ├── 1_040426_etoh_407_3.MOV
│   │   │   ├── 1_040426_etoh_408_1.MOV
│   │   │   └── ...
│   │   └── 2_040526_control\
│   │       └── ...
│   └── freeclimber_master\
│       └── (output CSV goes here)
```

The exact drive letter and root folder do not matter — just keep the structure consistent.

---

## 7. Installing the software

Open **Anaconda Prompt** (search "Anaconda Prompt" in the Start menu).

### Clone the repositories

Navigate to where you want the code to live (e.g., your user folder):

```
cd C:\Users\YourName
```

Clone both repos:

```
git clone https://github.com/jordanvasu/FreeClimber-FNG.git
git clone https://github.com/jordanvasu/FreeClimber-FNG-batch.git
```

### Create the Python environment

Navigate into the FreeClimber-FNG folder:

```
cd FreeClimber-FNG
```

Create a conda environment using the provided configuration file:

```
conda env create -f meta.yaml
```

This will take several minutes. When it finishes, activate the environment:

```
conda activate freeclimber
```

(The environment name may be different — check the output of the previous command to see what name was created.)

Install the two additional packages needed by the batch scripts:

```
pip install opencv-python ffmpeg-python
```

### Verify the installation

Run:

```
python -c "import trackpy, ffmpeg, cv2, scipy, pandas; print('OK')"
```

If you see `OK`, you are ready to process videos. If you see an error, re-read this section and confirm you activated the correct environment.

---

## 8. Selecting ROIs

Each video needs a configuration file (`.cfg`) that tells FreeClimber-FNG where in the frame the vial is located. The `roi_selector.py` script creates these files interactively.

Activate your conda environment (if not already active):

```
conda activate freeclimber
```

Navigate to the batch-scripts repo:

```
cd C:\Users\YourName\FreeClimber-FNG-batch
```

Run the ROI selector on one of your video folders:

```
python roi_selector.py "D:\project_freeclimber\data\video_data\1_040426_etoh"
```

A window will open showing the first frame of the first video. Click and drag a rectangle tightly around the vial — the top of the rectangle should sit just above the top of the vial, the bottom just below the bottom. Include a small margin on the left and right. Press **Enter** or **Space** to confirm. The window will immediately load the next video.

If you need to skip a video (bad frame, unusable footage), press **Escape**. The script will not write a `.cfg` file for that video, and you can come back to it later.

When all videos in the folder have been processed, the script prints a summary and exits. Repeat for each video folder.

Each `.cfg` file is saved next to its corresponding video, with the same filename stem. You can inspect them in VS Code if you want to verify the coordinates.

---

## 9. Batch processing

Still in the `FreeClimber-FNG-batch` folder, run the batch processor:

```
python batch_process.py "D:\project_freeclimber\data\video_data\1_040426_etoh" "D:\project_freeclimber\data\freeclimber_master"
```

The first argument is the folder containing your videos and `.cfg` files. The second argument is where the master CSV should be saved.

The script loops through every video in the input folder, runs the full FreeClimber-FNG pipeline, parses the filename into metadata columns (group, date, condition, fly_id, trial), and appends the results to `master_fng.csv`. Videos that fail processing are logged but do not stop the batch.

Expect this to take roughly 30-60 seconds per video, depending on your computer. A folder of 60 videos will take 30-60 minutes. You can leave it running unattended.

When it finishes, the script prints a summary: how many videos succeeded, how many failed, and the path to the master CSV.

If you are processing multiple groups, run the batch processor once per group folder. Each run appends to the master CSV rather than overwriting it.

---

## 10. What the batch script does

This section is informational — you do not need to read it to use the pipeline.

The batch processor wraps the core FreeClimber-FNG analysis in a loop. For each video, it loads the matching `.cfg` file, runs the detection pipeline (spot detection, vial assignment, filtering, FNG event detection, recovery speed calculation), reads the resulting `.fng.csv` output, adds five columns parsed from the filename, and concatenates the result into the master CSV. It logs any videos that fail with an exception rather than halting the batch.

The output `master_fng.csv` contains one row per detected FNG event, with columns identifying the fly and trial, the event's frame indices, fall magnitude in pixels and centimeters, fall duration in frames and seconds, and recovery duration in frames and seconds. See the FreeClimber-FNG repo documentation for detailed column definitions.

---

## 11. Troubleshooting

**"No module named cv2"** — You did not activate the conda environment, or you did not install `opencv-python`. Run `conda activate freeclimber` and `pip install opencv-python`.

**"ffmpeg not found"** — FFmpeg is not on your system PATH. Reinstall FFmpeg and make sure to check the "Add to PATH" option during installation. Restart Anaconda Prompt after installing.

**ROI selector window does not appear** — This sometimes happens on multi-monitor setups. Check your other monitors. If still missing, minimize all other windows and try again.

**Batch processor reports videos failing** — Check that every video in the folder has a matching `.cfg` file. Open one of the failing videos' `.cfg` files and verify the ROI coordinates look reasonable. If a video was heavily corrupted or the ROI was selected incorrectly, re-run the ROI selector on that video.

**Master CSV is empty or missing columns** — Make sure your filenames follow the `group_date_condition_flyid_trial` convention exactly. Extra or missing underscores will cause parsing failures.

**Out-of-memory errors** — Your ROI is too large (capturing most of the full 1920×1080 frame). Re-select the ROI with a tighter crop around the vial.

