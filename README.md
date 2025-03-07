This project is for an AI to take in a csv file through a desktop application and return grades for the data.

Authors: Colton Matthews, Dale Kanikkeberg, Ethan Deister, Kasyn Tang, Sage Markwardt

To run this file in VSCode: 
pip install pyqt5 groq pandas dotenv
python main.py

Create a config.env file following the guidelines within example.env using your personal API key. 

To create main.exe
in your ide terminal 
this worked for pycharm
1. pip install pyinstaller

2. pyinstaller --onedir --windowed --add-data "styles/styles.qss;styles" --add-data "config.env;." --add-data "default_settings.py;."   main.py  