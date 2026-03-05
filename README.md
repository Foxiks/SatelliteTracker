# SatelliteTracker
Simple SatelliteTracker with OpenStreetMaps / GoogleMaps

### Install Dependencies and Usage (Windows / Linux)
```
python3 -m pip install -r requirements.txt
python3 tracker.py
```

### Windows Binaries
Get the pre-built image of the program in the releases section!

### Build for Windows (Py3 module Nuitka and GCC Compile)
```
python3 -m pip install -r requirements.txt
python3 -m nuitka --standalone --mingw64 --enable-plugin=tk-inter tracker.py
```
```
move tle_data.txt, icon.png, numbers.json > tracker.dist
cd tracker.dist
... and run tracker.exe!
```

### Main Window
![1](/img/1.png)

![2](/img/2.png)

![3](/img/3.png)