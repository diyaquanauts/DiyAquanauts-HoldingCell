import cv2

# Open the video file
dirPath = "C:\\Users\\kmlan\\Downloads\\HawaiiFootage - Copy\\"
input_path = dirPath + 'rec_13-31-52.mp4'
cap = cv2.VideoCapture(input_path)

# Check if the video file was opened successfully
if not cap.isOpened():
    print("Error: Could not open video file.")
    exit()

# Get video properties
fps = int(cap.get(cv2.CAP_PROP_FPS))
frame_size = (
    int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
    int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
)

# Create a VideoWriter object for the output video
output_path = 'output.mp4'
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, fps, frame_size)

while True:
    ret, frame = cap.read()

    if not ret:
        break

    # Rotate the frame by 180 degrees
    rotated_frame = cv2.rotate(frame, cv2.ROTATE_180)

    # Write the rotated frame to the output video
    out.write(rotated_frame)

    # Display the rotated frame (optional)
    cv2.imshow('Rotated Video', rotated_frame)

    # Exit the loop when 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release video objects
cap.release()
out.release()
cv2.destroyAllWindows()
