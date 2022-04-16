# SHOME

This project helps to change your room ambience according to the user using facial recognition.

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