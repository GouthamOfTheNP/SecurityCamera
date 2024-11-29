# Security Camera Project

## Overview
The Security Camera Project is designed to provide motion detection and real-time video streaming capabilities, using Python, OpenCV, and PyQt6. The software is integrated with a live video feed server, email notifications, and advanced features like motion detection and video processing, making it an essential part of security camera solutions.

This project is part of a future commercial product but is available under the MIT License for open usage. While the software can be used freely, the end product should not be redistributed in any form.

## Prototype Link
Explore the live prototype: [Vigilance Solutions Prototype](https://vigilancesolutions.pythonanywhere.com/)

## Features
- **Live Video Streaming**: Real-time video streaming capabilities with personalized feeds for each user.
- **Motion Detection**: Detects and captures movement, sending email notifications in case of activity.
- **Frame Extraction and Video Processing**: Optimized to ensure smooth performance even in low-bandwidth environments.
- **Secure User Authentication**: Enhanced login form with secure password fields for better data protection.
- **Add Camera Button**: New feature to easily add cameras to the system, allowing for quick setup and configuration.

## Installation
To run this project locally, you will need Python 3.x and the required dependencies:

1. Clone this repository:
    ```bash
    git clone https://github.com/GouthamOfTheNP/security-camera-project.git
    cd security-camera-project
    ```
2. Set up a virtual environment (optional but recommended):
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3.	Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4. Run the application:
    ```bash
    python main.py
    ```

## Contributing
We welcome contributions to improve the project! If you'd like to contribute:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature-name`).
3. Make your changes and commit (`git commit -am 'Add feature'`).
4. Push to the branch (`git push origin feature-name`).
5. Submit a pull request explaining your changes.

Please ensure your contributions align with the project's goals, and that they follow the coding conventions.

**Note:** Since this project is part of a commercial product, while the software is open-source, the redistribution of the final bundled hardware or software product is prohibited.
