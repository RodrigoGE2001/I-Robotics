"""Detect people using YOLOv3 Tiny and track them using SORT."""

import cv2
import numpy as np
from sort import Sort


def object_tracking():
    """Upload a video file and use its frames to apply Yolo."""
    # Open video capture
    cap = cv2.VideoCapture("test.mp4")

    # Load YOLOv3 Tiny
    net = cv2.dnn.readNet("yolov3-tiny.weights", "yolov3-tiny.cfg")
    output_layers = net.getUnconnectedOutLayersNames()

    # Initialize SORT tracker
    mot_tracker = Sort()

    while True:
        # Read frame from video
        ret, frame = cap.read()
        if not ret:
            break

        # Prepare frames
        blob = cv2.dnn.blobFromImage(
            frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False
        )
        net.setInput(blob)
        outs = net.forward(output_layers)

        # Prepare thresholds, class IDs and bounding boxes
        class_ids = []
        confidences = []
        boxes = []
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.35 and class_id == 0:  # Person class
                    center_x = int(detection[0] * frame.shape[1])
                    center_y = int(detection[1] * frame.shape[0])
                    w = int(detection[2] * frame.shape[1])
                    h = int(detection[3] * frame.shape[0])
                    # Adjust bounding box from the center
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    w = int(w * 1.5)
                    h = int(h * 1.5)
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        # Apply NMS
        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

        dets = []

        # Draw bounding boxes
        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i]
                dets.append([x, y, x + w, y + h, 1.0])
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
                cv2.putText(
                    frame,
                    "Personita",
                    (x, y - 10),
                    cv2.FONT_HERSHEY_PLAIN,
                    2,
                    (0, 0, 255),
                    thickness=2,
                )

        trackers = mot_tracker.update(np.array(dets))

        # Draw trackin g results
        for d in trackers:
            x1, y1, x2, y2, track_id = map(int, d)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 3)

        # Display frame with tracking information
        cv2.imshow("view", frame)

        # Check for Esc key
        key = cv2.waitKey(1)
        if key == 27:
            break

    # Close windows and program
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    """Begin program."""
    object_tracking()
