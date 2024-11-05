# Security Camera Project



## A software project for detecting and capturing movement ##

The Security Camera Project is a comprehensive solution designed for motion detection and video capture, aimed at enhancing surveillance systems. This software leverages webcam technology to monitor designated areas, detect any movement, and record video footage when activity is identified. Key functionalities include frame extraction, video processing, and the ability to send recorded footage via email.

### Key Features:
- **Motion Detection**: The software continuously monitors video streams and triggers recordings only when movement is detected, optimizing storage and processing resources.
- **Frame Extraction**: Captured video frames are analyzed, and rectangular regions of interest are identified to isolate the most relevant parts of the footage.
- **Video Processing**: After detecting movement, the system extracts and merges video segments, creating a final video that highlights the identified activity.
- **Email Integration**: The recorded video footage can be automatically sent to a predefined email address for remote monitoring, using the self-developed `SendEmailPy3` library.
- **Customizability**: Users can configure parameters such as motion sensitivity, video length, and email notification settings to meet their specific security needs.

### Commercial Use Notice

This project is part of a commercial product. While the software itself is open source and can be freely used, the final product created from this software cannot be redistributed or sold without permission. The intention is to provide individuals and businesses with customizable security software, but the end product remains under restricted distribution.

### How It Works:
1. **Continuous Video Monitoring**: The software runs continuously, capturing real-time footage from a connected webcam.
2. **Movement Detection**: Using image processing techniques, the system detects when an object or person moves within the camera's field of view.
3. **Video Creation**: Once movement is detected, the software captures the relevant footage, processes the video, and merges segments to create a complete video.
4. **Email Alerts**: After processing, the software automatically sends the video to a specified email for immediate access to the recording.

### Technologies Used:
- **Python**: Core programming language used to develop the project.
- **OpenCV**: For video capture, motion detection, and frame processing.
- **SendEmailPy3**: For sending the recorded video via email notifications.
- **Flask**: For creating a user-friendly web interface that allows for users to sign up and view their camera footage.
- **PyQt6**: For creating a desktop GUI that allows a user-friendly program for accessing databases.

### License

This project is licensed under the MIT License, allowing for open usage of the source code with attribution.
