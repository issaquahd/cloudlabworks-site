#!/usr/bin/env python3
"""Whiten teeth in a video: MediaPipe face landmarks -> inner-lip polygon -> teeth pixels
(bright, low-saturation, warm hue) inside it -> desaturate and lift, feathered.
Usage: whiten.py in.mp4 out.mp4 [--sat 0.35] [--lift 1.08] [--debug dir]
"""
import sys, subprocess, json, os
import numpy as np, cv2
import mediapipe as mp

INNER_LIPS = [78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308, 415, 310, 311, 312, 13, 82, 81, 80, 191]

def main():
    src, dst = sys.argv[1], sys.argv[2]
    sat = float(sys.argv[sys.argv.index("--sat") + 1]) if "--sat" in sys.argv else 0.35
    lift = float(sys.argv[sys.argv.index("--lift") + 1]) if "--lift" in sys.argv else 1.08
    dbg = sys.argv[sys.argv.index("--debug") + 1] if "--debug" in sys.argv else None
    probe = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate", "-of", "json", src]))["streams"][0]
    W, H = probe["width"], probe["height"]; fps = probe["r_frame_rate"]
    lm = mp.solutions.face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5)
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", fps, "-i", "-",
                            "-i", src, "-map", "0:v", "-map", "1:a?", "-c:v", "libx264", "-preset", "slow", "-crf", "21", "-pix_fmt", "yuv420p",
                            "-movflags", "+faststart", "-c:a", "copy", dst], stdin=subprocess.PIPE)
    n = 0; hit = 0; px_total = 0
    fps_num, fps_den = (int(x) for x in fps.split("/"))
    while True:
        buf = dec.stdout.read(W * H * 3)
        if len(buf) < W * H * 3: break
        frame = np.frombuffer(buf, np.uint8).reshape(H, W, 3).copy()
        ts_ms = int(n * 1000 * fps_den / fps_num)
        res = lm.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if res.multi_face_landmarks:
            L = res.multi_face_landmarks[0].landmark
            pts = np.array([[L[i].x * W, L[i].y * H] for i in INNER_LIPS], np.int32)
            poly = np.zeros((H, W), np.uint8); cv2.fillPoly(poly, [pts], 255)
            poly = cv2.dilate(poly, np.ones((3, 3), np.uint8))
            if poly.any():
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).astype(np.float32)
                h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
                teeth = (poly > 0) & (v > 110) & (s < 120) & ((h < 35) | (h > 160))
                m = teeth.astype(np.float32)
                m = cv2.GaussianBlur(m, (0, 0), 1.2)
                if m.max() > 0:
                    hit += 1; px_total += int(teeth.sum())
                    s2 = s * (1 - m * (1 - sat))
                    v2 = np.minimum(255, v * (1 + m * (lift - 1)))
                    hsv[..., 1] = s2; hsv[..., 2] = v2
                    frame = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
                    if dbg and n % 24 == 0:
                        d = frame.copy(); cv2.polylines(d, [pts], True, (0, 0, 255), 1); cv2.imwrite(os.path.join(dbg, f"dbg_{n:04d}.jpg"), d)
        enc.stdin.write(frame.tobytes()); n += 1
    enc.stdin.close(); enc.wait(); dec.wait()
    print(f"frames {n}, frames with teeth {hit}, teeth pixels total {px_total}")

if __name__ == "__main__":
    main()
