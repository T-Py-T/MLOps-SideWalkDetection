import cv2
import os
import numpy as np
import time
from PIL import Image
from tflite_runtime.interpreter import Interpreter

class CNN:

	def __init__(self, model):
		self.interpreter = Interpreter(model_path=model)
		self.interpreter.allocate_tensors()
		# get model details 
		self.input_details = self.interpreter.get_input_details()
		self.output_details = self.interpreter.get_output_details()
		self.floating_model = self.input_details[0]['dtype'] == np.float32
		self.height = self.input_details[0]['shape'][1]
		self.width = self.input_details[0]['shape'][2]
		self.model_in_mean = 127.5
		self.model_in_std = 127.5

	def classify_image(self, image):
		
		h,w,c=image.shape

		if h!=self.height or w!=self.width:
			image = cv2.resize(image, (self.width, self.height), interpolation = cv2.INTER_AREA)

		# add N dim
		input_data = np.expand_dims(image, axis=0)

		if self.floating_model:
  			input_data = (np.float32(input_data) - self.model_in_mean) / self.model_in_std
		self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
		self.interpreter.invoke()

		output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
		return np.squeeze(output_data)
