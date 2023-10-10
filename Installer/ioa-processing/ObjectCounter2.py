import cv2
from fileGuiOperations import fileSelection
import random
import time

class ObjectCounter:
    frame_count = 0

    def __init__(self, video_path, frame_interval=30):
        self.video_path = video_path
        self.frame_interval = frame_interval
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2()

    def count_objects(self):
        cap = cv2.VideoCapture(self.video_path)
        self.frame_count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            self.frame_count += 1
            if self.frame_count % self.frame_interval == 0:
                fg_mask = self.background_subtractor.apply(frame)
                _, binary_mask = cv2.threshold(fg_mask, 127, 255, cv2.THRESH_BINARY)
                contours, hierarchy = cv2.findContours(binary_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

                object_count = 0
                for i, contour in enumerate(contours):
                    area = cv2.contourArea(contour)
                    if area > 50:  # Adjust the threshold as needed
                        object_count += 1
                        # Generate a random color for the outline
                        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                        # Make the contour outline thinner
                        cv2.drawContours(frame, contours, i, color, 1)

                        # Check for parent-child relationship in hierarchy
                        if hierarchy[0][i][3] != -1:
                            # This contour has a parent, likely an overlapping object
                            parent_index = hierarchy[0][i][3]
                            cv2.drawContours(frame, contours, parent_index, (0, 0, 255), 1)  # Draw parent in red

                yield object_count, frame

        cap.release()

# Usage
fileOps = fileSelection()

video_path = fileOps.selectFile("mp4")

frame_interval = 5
object_counter = ObjectCounter(video_path, frame_interval)

for object_count, frame in object_counter.count_objects():
    print(f'Frame: {object_counter.frame_count}, Objects: {object_count}')

    # Display or save the frame with object outlines
    cv2.imshow('Outlined Objects', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    #time.sleep(0.1)

cv2.destroyAllWindows()
