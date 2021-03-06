import torch
import os
from torch.utils.data import Dataset
from PIL import Image
import numpy as np
from config import TRAIN_CAP, TEST_CAP
import random

class AwA2Dataset(Dataset):
	def __init__(self, images_dir, label_file, attribute_file, train_cap=TRAIN_CAP, test_cap=TEST_CAP, split=None, transforms=None):
		self.name = 'awa2'

		self.images_dir = images_dir
		self.label_file = label_file
		self.transforms = transforms
		self.split = split
		self.train_cap = train_cap
		self.test_cap = test_cap

		self.images = []
		self.labels = []
		self.attributes = []

		with open(self.label_file, 'r') as f:
			for line in f.readlines():
					class_id = line.split()[1]
					self.labels.append(class_id)

		for item in os.listdir(self.images_dir):
			for f in os.listdir(self.images_dir+item+"/"):
					self.images.append(self.images_dir+item+'/'+f)

		with open(attribute_file, 'r') as f:
			for line in f.readlines():
					attributes = line.split()
					attributes = [float(x) for x in attributes]
					self.attributes.append(attributes)
		
		random.shuffle(self.images)		
		self.train_images = self.images[: self.train_cap]
		self.test_images = self.images[self.train_cap : self.train_cap + self.test_cap]
		self.dump_train_image_paths('../Animals_with_Attributes2/train_image_paths.txt')
		self.dump_test_image_paths('../Animals_with_Attributes2/test_image_paths.txt')

	def dump_train_image_paths(self, filename):
		with open(filename, 'w') as f:
			for img_path in self.train_images:
					f.write(img_path+'\n')
	
	def dump_test_image_paths(self, filename):
		with open(filename, 'w') as f:
			for img_path in self.test_images:
				f.write(img_path+'\n')
			
	def __len__(self):
		if self.split == 'train':
			return len(self.train_images)
		
		if self.split == 'test':
			return len(self.test_images)

	def __getitem__(self, idx):
		image, one_hot = None, None
		attribute = None

		if self.split == 'train':
			img_path = self.train_images[idx]
			cls_label = img_path.split('/')[3]
			label = int(self.labels.index(cls_label))
			attribute = self.attributes[label]
			one_hot = float(label)

		if self.split == 'test':
			img_path = self.test_images[idx]
			cls_label = img_path.split('/')[3]
			label = int(self.labels.index(cls_label))
			attribute = self.attributes[label]
			one_hot = float(label)

		one_hot = torch.tensor(one_hot)
		image = np.array(Image.open(img_path).convert('RGB'))
		if self.transforms is not None:
			image = self.transforms(image=image)['image']
		return image, torch.tensor(attribute), one_hot


