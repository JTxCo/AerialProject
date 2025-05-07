'''
    This is the script for testing out getting the SpaceNet data.
    
    Located: aws s3 ls --no-sign-request s3://spacenet-dataset
    
    Terms: AOIs: Areas of Interest
    

'''

import os
import torch
from torch import rand
img = rand(1,3,1024,1024, device="mps", dtype=torch.bfloat16)
out = model(img)

