# Quiz Millionaire Challenge

## Overview
The Quiz Millionaire Challenge is an engaging trivia game inspired by the popular game show "Who Wants to Be a Millionaire?". This Python-based desktop application challenges players with a series questions as they attempt to win a virtual million dollars. It features multiple choice questions, various lifelines to assist the player, and dynamic question generation using the Ollama API.

## Features
- **Dynamic Question Generation**: Leverages the Ollama API to generate unique and challenging questions.
- **Lifelines**: Three lifelines including "50:50", "Phone a Friend", and "Ask the Audience" help players through difficult questions.

## System Requirements
- **Python 3.8+**: Ensure Python is installed and correctly set up on your system.
- **Ollama API**: Required for fetching and generating questions.
- **NVIDIA GPU**: Recommended for optimal performance, particularly for any AI-driven features.
- **FFmpeg**: Required for handling multimedia content.

## Installation Guide

### Step 1: Download the Game
Download the ZIP file containing the game from the Releases section of this GitHub repository. Extract the contents of the ZIP file to a directory of your choice.

### Step 2: Install Dependencies
1. **Python**: Make sure Python is installed on your machine. If not installed, download and install it from [Python's official website](https://www.python.org/downloads/).

2. **Ollama Setup**: You must have the Ollama API set up and running. This typically involves installing Ollama software from their official website and ensuring it is configured to run locally on your machine.

3. **NVIDIA GPU Drivers**: Ensure that your NVIDIA drivers are up to date to maximize performance, particularly if you are using features that require GPU acceleration.

### Step 3: Run the Installation Script
Navigate to the directory where you extracted the game files and double-click on the `start.bat` file. This batch file will:
- Check if all necessary software (like Python and FFmpeg) is installed.
- Set up a Python virtual environment.
- Install all required Python dependencies from `requirements.txt`.
- Verify the installation of the Ollama API and model.
- Start the game.

### Step 4: Play the Game
Once the installation script completes successfully, the game will launch, and you can start playing the Quiz Millionaire Challenge immediately.

## Troubleshooting
If you encounter issues during the installation or while playing the game:
- Ensure all prerequisites are installed and properly configured.
- Check the console output for any error messages that may indicate what went wrong.
- Refer to the Ollama API documentation for troubleshooting common issues with Ollama setup.

Enjoy testing your knowledge and climbing to the virtual millionaire status!

