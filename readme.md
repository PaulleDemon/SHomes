# SHOME

This project helps to change your room ambience according to the user using facial recognition. This is just a prototype not a complete product. Read the code and modify it according to your needs.

We make use of facial-recognition library to detect faces, currently the `face_location` model is set to 'cnn'. which can be slow, but more accurate, where as hog is less accurate but fast.

Please create a new folder called data and place it in root folder, the data folder must contain data.json and imagedata folder as shown below.

```

SHome/
    ├── ardunio/
    ├── GUI/
    └── data/
        ├── data.json
        └── imagedata/
            └── example.png
```

> Note: please do the connections based on the ardunio code provided in the ardunio folder
# Usage instruction

![demo](https://github.com/PaulleDemon/SHomes/blob/master/demoimages/iot-project-demo.jpg)
1. run main.py from GUI folder
2. Click on start capture button in the left panel.
3. Click on the capture frame button, you will be presented with a rectangular draw tool, please use it to mark face. A preview will be generated on the right panel.
4. select preferences, and in set image name include only the name of the file.
5. Thats it now whenever it detects a saved face, it will change the room ambience.
