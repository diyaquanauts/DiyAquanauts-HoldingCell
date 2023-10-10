import cv2
from fileGuiOperations import fileSelection
import os
import random
import time


class SimpleObjectCounter:
    frameIndex = 0
    imageDir

    def __init__(self, vidPath, frameInterval=10, imageDir = "output_images"):
        self.vidPath = vidPath
        self.imageDir = imageDir
        self.frameInterval = frameInterval
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2()

    def count_objects(self):
        cap = cv2.VideoCapture(self.vidPath)
        self.frameIndex = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            self.frameIndex += 1
            if self.frameIndex % self.frameInterval == 0:
                fg_mask = self.background_subtractor.apply(frame)
                _, binary_mask = cv2.threshold(fg_mask, 127, 255, cv2.THRESH_BINARY)
                contours, _ = cv2.findContours(
                    binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
                )

                objCount = 0
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if area > 50:  # Adjust the threshold as needed
                        objCount += 1
                        # Generate a random color for the outline
                        color = (
                            random.randint(0, 255),
                            random.randint(0, 255),
                            random.randint(0, 255),
                        )
                        # Make the contour outline thinner
                        cv2.drawContours(frame, [contour], -1, color, 1)
                yield objCount, frame
        cap.release()

    def saveAnnotatedImg(self, image, frameIndex, objCount):
        # Convert the image to BGR color format
        image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Define the font properties
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.9
        font_color = (255, 255, 0)  # Yellow color in RGB
        font_thickness = 1
        font_line_type = cv2.LINE_AA

        # Define the text to display
        text = f"Frame: {frameIndex}, Objects: {objCount}"

        # Calculate text size and position
        text_size, _ = cv2.getTextSize(text, font, font_scale, font_thickness)
        text_x = 10  # X-coordinate for the top-left corner of the text
        text_y = 10 + text_size[1]  # Y-coordinate for the top-left corner of the text

        # Add red outline to the text
        outline_thickness = 2  # You can adjust the thickness as needed

        cv2.putText(
            image_bgr,
            text,
            (text_x, text_y),
            font,
            font_scale,
            (255, 0, 0),  # Red in RGB
            outline_thickness,
            font_line_type,
        )

        # Add the text in yellow
        cv2.putText(
            image_bgr,
            text,
            (text_x, text_y),
            font,
            font_scale,
            font_color,
            font_thickness,
            font_line_type,
        )

        # Convert back to RGB color format
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

        # Save the image with the frame index number
        os.makedirs(self.imageDir, exist_ok=True)
        output_file = os.path.join(self.imageDir, f"frame_{frameIndex}.jpg")
        cv2.imwrite(output_file, image_rgb)

        return image_rgb

    def reassembleVideoFromImages(self, outputPath, fps=30):
        image_files = sorted(os.listdir(self.imageDir))
        if not image_files:
            print("No image files found in the directory.")
            return

        # Read the first image to get dimensions
        first_image = cv2.imread(os.path.join(self.imageDir, image_files[0]))
        height, width, _ = first_image.shape

        # Initialize the video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(outputPath, fourcc, fps, (width, height))

        previous_frame_number = None
        previous_frame = None

        for image_file in image_files:
            frame_number = int(image_file.split("_")[1].split(".")[0])

            # Fill the gap with the previous frame if needed
            if previous_frame_number is not None:
                for _ in range(frame_number - previous_frame_number - 1):
                    out.write(previous_frame)

            # Read and write the current frame
            current_frame = cv2.imread(os.path.join(self.imageDir, image_file))
            out.write(current_frame)

            previous_frame_number = frame_number
            previous_frame = current_frame

        # Release the video writer
        out.release()
        print(f"Video saved to {outputPath}")


# Usage
fileOps = fileSelection()

vidPath = fileOps.selectFile("mp4")

frameInterval = 4
objCounter = SimpleObjectCounter(vidPath, frameInterval)

for objCount, frame in objCounter.count_objects():
    print(f"Frame: {objCounter.frameIndex}, Objects: {objCount}")

    # Display or save the frame with object outlines
    annotatedImg = objCounter.saveAnnotatedImg(frame, objCounter.frameIndex, objCount)
    cv2.imshow("Outlined Objects", annotatedImg)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
    # time.sleep(0.01)

# Usage
#imageDirectory = "output_images"  # Directory containing annotated images
output_video_path = "output_video.mp4"  # Desired output video file path
fps = 30  # Frames per second for the output video

objCounter.reassembleVideoFromImages(output_video_path, fps)

cv2.destroyAllWindows()
