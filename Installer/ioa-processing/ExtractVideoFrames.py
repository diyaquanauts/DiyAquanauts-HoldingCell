import cv2
from fileGuiOperations import fileSelection


class VideoFrameExtractor:
    def extract_frames(self, video_path, frame_interval=30):
        cap = cv2.VideoCapture(video_path)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        frame_count = 0
        frame_number = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            if frame_count % frame_interval == 0:
                frame_number += 1
                output_filename = f'output_frame_{frame_number:04d}.jpg'
                cv2.imwrite(output_filename, frame)
                print(f'Frame {frame_number} saved as {output_filename}')

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

# Usage
fileOps = fileSelection()
frame_extractor = VideoFrameExtractor()

video_path = fileOps.selectFile("mp4")
frame_interval = 30

frame_extractor.extract_frames(video_path, frame_interval)
