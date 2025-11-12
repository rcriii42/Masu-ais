# Masu-ais
Download and process dredge ais data from [NOAA](https://hub.marinecadastre.gov/pages/vesseltraffic)

Download the source code:

PS C:\Users\you\PycharmProjects> git clone https://github.com/rcriii42/Masu-ais.git Masu-ais

Change to the Masu-ais directory and create a virtual environment (not required but recommended):

PS C:\Users\you\PycharmProjects\Masu_ais> python -m venv .\env

Activate the virtual environment:

* In Bash (Linux, Unix, etc): source env/bin/activate
* In Windows Powershell: env\scripts\activate.ps1
* Commands for other command-line environments [here](https://docs.python.org/3/library/venv.html#creating-virtual-environments) (scroll down to the table)
After activating the virtual environment, the command prompt will be preceded by (env) .

Install the requirements: (env) PS C:\Users\you\PycharmProjects\Masu-ais> pip install -r requirements.txt

The first time you run the script it will create two subdirectories:

* all_ais_data: Holds the downloaded single day files with all vessel AIS data
* vessel_ais_data: Holds the generated single-vessel AIS files
