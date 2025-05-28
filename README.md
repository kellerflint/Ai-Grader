# AI Grade Calculator

This project uses AI to process a CSV file through a desktop application and returns grades for the data.

## Authors
- Colton Matthews
- Dale Kanikkeberg
- Ethan Deister
- Kasyn Tang
- Sage Markwardt

## Requirements

Make sure you have the following Python packages installed:

```bash
pip install pyqt5 groq pandas python-dotenv QtAwesome matplotlib
```

## Running the Application

To run the application in VSCode:

Install the necessary dependencies:

```bash
pip install pyqt5 groq pandas python-dotenv pyqtgraph
```

Run the application:

```bash
    python main.py
```

Setting Up API Key

Create a config.env file following the guidelines in the example.env file and insert your personal API key.

## Creating the Executable

If you're using PyCharm or VsCode and want to create an executable file, follow these steps:

Install PyInstaller:

```bash
pip install pyinstaller
```

Create the executable:

```bash
pyinstaller --onedir --windowed --add-data "styles/styles.qss;styles" --add-data "config.env;." --add-data "default_settings.py;." main.py
```

This command will generate the executable inside the dist/main directory. To run it, right-click the dist folder, choose "Open in Folder," and run the .exe file.

Issues with pyinstaller can potentially be fixed by using the following command instead:

```bash
Python -m PyInstaller --onedir --windowed --add-data "styles/styles.qss;styles" --add-data "config.env;." --add-data "default_settings.py;." main.py
```
