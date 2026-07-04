import cv2
import mediapipe as mp
from mediapipe.tasks.python import vision
from mediapipe.tasks import python
import random
import math

# ==========================
# MediaPipe Setup
# ==========================

model_path = "hand_landmarker.task"

base_options = python.BaseOptions(model_asset_path=model_path)

options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=2
)

detector = vision.HandLandmarker.create_from_options(options)

# ==========================
# CAMERA
# ==========================

camera = cv2.VideoCapture(0)

draw_points = []

fingertip_ids = [4, 8, 12, 16, 20]

# ==========================
# LOOP
# ==========================

while True:

    success, frame = camera.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb
    )

    result = detector.detect(mp_image)

    h, w, _ = frame.shape

    mode_lightning = False
    mode_chakra = False

    # ==========================
    # HAND PROCESSING
    # ==========================

    if result.hand_landmarks:

        for hand in result.hand_landmarks:

            # ==========================
            # GESTURES
            # ==========================

            peace_sign = (
                hand[8].y < hand[6].y and
                hand[12].y < hand[10].y and
                hand[16].y > hand[14].y and
                hand[20].y > hand[18].y
            )

            fire_gesture = (
                hand[8].y > hand[6].y and
                hand[12].y > hand[10].y and
                hand[16].y > hand[14].y and
                hand[20].y > hand[18].y
            )

            open_hand = (
                hand[8].y < hand[6].y and
                hand[12].y < hand[10].y and
                hand[16].y < hand[14].y and
                hand[20].y < hand[18].y
            )

            # ==========================
            # MODE CONTROL
            # ==========================

            if open_hand:
                draw_points.clear()

            elif peace_sign:
                mode_lightning = True

            elif fire_gesture:
                mode_chakra = True

            # ==========================
            # FINGERTIPS (BLACK DOTS)
            # ==========================

            points = []

            for tip in fingertip_ids:

                px = int(hand[tip].x * w)
                py = int(hand[tip].y * h)

                points.append((px, py))

                cv2.circle(frame, (px, py), 3, (0, 0, 0), -1)

            # ==========================
            # ⚡ TWISTED SPARK LIGHTNING (UPDATED)
            # ==========================

            if mode_lightning:

                x1 = int(hand[8].x * w)
                y1 = int(hand[8].y * h)
                x2 = int(hand[12].x * w)
                y2 = int(hand[12].y * h)

                # create zig-zag twist effect
                for i in range(6):

                    t = i / 5

                    mx = int(x1 + (x2 - x1) * t)
                    my = int(y1 + (y2 - y1) * t)

                    offset = random.randint(-10, 10)

                    sx = mx + offset
                    sy = my + offset

                    cv2.circle(frame, (sx, sy), 2, (255, 255, 255), -1)

                    if i > 0:
                        cv2.line(frame,
                                 (prev_x, prev_y),
                                 (sx, sy),
                                 (255, 255, 255),
                                 2)

                    prev_x, prev_y = sx, sy

                # main glow line
                cv2.line(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)

                # spark burst
                for _ in range(6):
                    sx = x2 + random.randint(-20, 20)
                    sy = y2 + random.randint(-20, 20)
                    cv2.circle(frame, (sx, sy), 2, (255, 255, 255), -1)

                cv2.putText(frame, "SPARK LIGHTNING",
                            (30, 80),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1,
                            (255, 255, 255),
                            3)

            # ==========================
            # CHAKRA MODE (UNCHANGED)
            # ==========================

            elif mode_chakra:

                cx = int(hand[9].x * w)
                cy = int(hand[9].y * h)

                angle = cv2.getTickCount() % 360

                for i in range(6):

                    theta = math.radians(angle + i * 60)

                    ox = int(cx + math.cos(theta) * 50)
                    oy = int(cy + math.sin(theta) * 50)

                    cv2.circle(frame, (ox, oy), 8, (255, 255, 255), -1)

                cv2.circle(frame, (cx, cy), 25, (255, 255, 255), -1)

                cv2.putText(frame, "CHAKRA MODE",
                            (30, 140),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1,
                            (255, 255, 255),
                            3)

            # ==========================
            # NORMAL TRAIL
            # ==========================

            if not mode_lightning and not mode_chakra:

                x = int(hand[8].x * w)
                y = int(hand[8].y * h)

                draw_points.append((x, y))

                if len(draw_points) > 300:
                    draw_points.pop(0)

                for i in range(1, len(draw_points)):
                    cv2.line(
                        frame,
                        draw_points[i - 1],
                        draw_points[i],
                        (255, 255, 255),
                        3
                    )

    # ==========================
    # FINGER CONNECTION (NORMAL ONLY)
    # ==========================

    if result.hand_landmarks and len(result.hand_landmarks) >= 2:

        if not mode_lightning and not mode_chakra:

            hand1 = result.hand_landmarks[0]
            hand2 = result.hand_landmarks[1]

            for tip in fingertip_ids:

                x1 = int(hand1[tip].x * w)
                y1 = int(hand1[tip].y * h)
                x2 = int(hand2[tip].x * w)
                y2 = int(hand2[tip].y * h)

                cv2.line(frame, (x1, y1), (x2, y2), (200, 200, 200), 2)

    # ==========================
    # UI
    # ==========================

    cv2.putText(frame, "GestureFX Spark Edition",
                (10, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 255),
                2)

    cv2.putText(frame, "ESC = Exit",
                (10, h - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2)

    cv2.imshow("GestureFX Spark Lightning", frame)

    if cv2.waitKey(1) == 27:
        break

camera.release()
cv2.destroyAllWindows()