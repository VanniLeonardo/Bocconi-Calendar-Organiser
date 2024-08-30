# Bocconi University Schedule Formatter

![Bocconi University](https://en.wikipedia.org/wiki/File:Bocconi_University_Logo.png)

## Table of Contents

- [Background](#background)
- [Installation](#installation)
- [Usage](#usage)
- [Contributors](#contributors)

## Background

For Bocconi University students, the official lecture schedule imported into Google Calendar can be confusing due to unclear lecture names and formatting issues. This project aims to simplify and improve the readability of the lecture schedule by taking the existing Google Calendar events (and in the future, directly fetching from Bocconi's systems) and generating a new, more user-friendly calendar with easy-to-understand lecture names, dates, and times.

## Installation

The installation process currently requires a few manual steps. Here's how you can set it up:

0. **Clone the Repository**: 
    - Start by cloning this repository to your local machine.
   ```bash
   git clone https://github.com/VanniLeonardo/Bocconi-Calendar-Organiser
   cd Bocconi-Calendar-Organiser
    ```

1. **Install Dependencies**: 
    - Use pip to install the required Python packages listed in the requirements.txt file. Ensure you have Python >= 3.10 installed.

    ```bash
    pip install -r requirements.txt
    ```

2. **Sync Bocconi Schedule with Google Calendar:**
    - **If** you do not already have the official Bocconi lecture schedule imported into Google Calendar, follow these steps:
        - Visit [youatb.unibocconi.it](https://youatb.unibocconi.it) and login
        - Retrieve the iCal URL of your lecture schedule.
        - Sync this iCal with your Google Calendar.
    - **Else**: Proceed to the next step if your Bocconi schedule is already synced with Google Calendar.

3. **Retrieve Google Calendar ID**:
    - Go to your Google Calendar and find the Calendar ID of your Bocconi lecture calendar. You can find this in the calendar settings under "Integrate Calendar."

4. **Configure Constants**:
    - Open the '***constants.py***' file.
    - Set the '***LECTURES_ID***' variable to the Google Calendar ID retrieved in the previous step.
    - Update the '***CLASSES***' list with the exact names, or part of them, of the courses you are interested in.
    - Map these lecture name to their full names in the '***REGEX_DICT***' dictionary.

## Usage

Once the setup is complete, you can run the application by executing:
    ```python schedule_scraper_app.py```