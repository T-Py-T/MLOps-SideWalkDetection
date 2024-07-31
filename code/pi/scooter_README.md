Code repository for Alpha2 scooter project.  Includes code for Raspberry Pi, PC,
and Google Colab, along with sample data, and sidewalk/street trained model

Quick summary of how to use this repository:

To collect data:

    1) Copy RPi code files and neural network model to RPi.
    2) Collect image data while riding scooter.  Label data while collecting with joystick.
    3) Download collected data folder to PC with WinSCP or other method.

To create video from collected image data:

    1) Run: python3 makeScooterVideo.py runFolder boxes
          boxes = 1:  annotate frames with classifier status
          boxes = 2:  annotate frames with joystick status
          boxes = 3:  annotate frames with classifier and joystick status

To train model with collected image data:

    1) Run: python3 sortLabeledImages.py runFolder
	       - if joystick and classifier agree, image will be in class subfolder
           - if joystick and classifier disagree, image will be in _class folder
           - manually verify images and where necessary, move to appropriate class folder

    2) Run: python3 createTrainingZip.py runFolder
    3) Upload training zip file to Google Drive along with .ipynb file from colab folder
    4) Run .ipynb file in Colab and follow included directions to train new model or 
       retrain existing model
    5) Download trained model from Google drive to PC, and then to RPi

Other tools:

    1) Run: python unsortImages runFolder
            - moves image files out of class sub-folders back to root folder
            - saves image classes to sort_results.txt file

	2) Run: python resortImages runFolder
            - moves image files from root folder to class sub-folders using
              information from sort_results.txt



