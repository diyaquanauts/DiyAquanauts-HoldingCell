import cv2
from fileGuiOperations import fileSelection
import json
import os
import random


class SimpleObjectCounter:
    frameIndex = 0
    imageDir = ""
    results = []

    def __init__(self, vidPath, frameInterval=10, imageDir="output_images"):
        self.vidPath = vidPath
        self.imageDir = imageDir
        self.frameInterval = frameInterval
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2()

        self._clearImageDir()

    def _clearImageDir(self):
        # Delete all files in the imageDir directory when the object is initialized
        files = os.listdir(self.imageDir)

        # Loop through the list of files and remove them one by one
        for filename in files:
            file_path = os.path.join(self.imageDir, filename)
            os.remove(file_path)

    # Contrast adjustment factor (1.0 is no change)
    # Brightness adjustment factor (positive for brighter, negative for darker)
    def countObjects(self, contrast=2.0, brightness = -70):
        cap = cv2.VideoCapture(self.vidPath)
        self.frameIndex = 0
        self.results = []

        while True:
            ret, frame = cap.read()
            frame = cv2.convertScaleAbs(frame, alpha=contrast, beta=brightness)
            if not ret:
                break
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

                self.results.append({ "frame": { "index": self.frameIndex, "objCount": objCount }})
                yield objCount, frame

            self.frameIndex += 1

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
        self.imageDir = "output_images"  # You can specify your desired output directory
        os.makedirs(self.imageDir, exist_ok=True)
        output_file = os.path.join(self.imageDir, f"frame_{frameIndex:08d}.png")
        cv2.imwrite(output_file, image_rgb)

        return image_rgb

    def reassembleVideoFromImages(self, outputPath, fps=30, frameInterval=4):
        imageFiles = sorted(os.listdir(self.imageDir))
        if not imageFiles:
            print("No image files found in the directory.")
            return
        # Read the first image to get dimensions
        firstImage = cv2.imread(os.path.join(self.imageDir, imageFiles[0]))
        height, width, _ = firstImage.shape

        # Initialize the video writer
        fourcc = cv2.VideoWriter_fourcc(*"H264")
        out = cv2.VideoWriter(outputPath, fourcc, fps, (width, height))

        frameIndexNumber = 0  # Initialize frame number

        for imageFile in imageFiles:
            # Read and write the current frame multiple times (frameInterval)
            currentFrame = cv2.imread(os.path.join(self.imageDir, imageFile))
            for _ in range(frameInterval):
                out.write(currentFrame)
                frameIndexNumber += 1
            # Ensure the first frame (frame_0) is written at least once
            if frameIndexNumber == 0 and frameInterval > 1:
                out.write(currentFrame)
                frameIndexNumber += 1
        # Release the video writer
        out.release()
        print(f"Video saved to {outputPath}")

    def saveResultsToJson(self, fileName):
        with open(fileName, "w") as json_file:
            json.dump(self.results, json_file)

# Usage
if __name__ == "__main__":
    fileOps = fileSelection()

    vidPath = fileOps.selectFile("mp4")

    frameInterval = 5
    objCounter = SimpleObjectCounter(vidPath, frameInterval)

    for objCount, frame in objCounter.countObjects():
        print(f"Frame: {objCounter.frameIndex}, Objects: {objCount}")

        # Display or save the frame with object outlines
        annotatedImg = objCounter.saveAnnotatedImg(
            frame, objCounter.frameIndex, objCount
        )
        cv2.imshow("Outlined Objects", annotatedImg)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        # time.sleep(0.01)

    cv2.destroyAllWindows()

    print("Generating video file...")

    output_video_path = "output_video.mp4"  # Desired output video file path
    fps = 30  # Frames per second for the output video

    objCounter.reassembleVideoFromImages(output_video_path, fps)

    print("Dumping results to JSON...")

    results_file_path = "object_count_results.json"  # Desired JSON file path
    objCounter.saveResultsToJson(results_file_path)
