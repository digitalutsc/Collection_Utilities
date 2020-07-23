#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import os
import re


# In[2]:


#Global variables
image_pid_column_name = 'mods_URI_PID'
rotate_info_column_name = 'Process Orientation'
REGEX = r'^Rotate (.*) (CW|CCW)$'
images_source_dir = ""
images_target_dir = ""
metadata_file = "data/metadata.csv"


# In[3]:


# Lookup a column value by another column name and value in a dataframe
def lookup_df_value_column_value(df, key_col, key_val, val_col, idx=0):
    try:
        result_df = df.loc[df[key_col] == key_val].iloc[0]
        value = result_df[val_col]
        return value
    except IndexError:
        return 0


# In[4]:


def rotate_image(image_filename, pid, metadata_df):
    # Get the photoservice number and search for it in the 
    split_rotation_value = lookup_df_value_column_value(metadata_df, image_pid_column_name, pid, rotate_info_column_name, idx=0)
    if str(split_rotation_value) == "0":
        print("Not able to rotate " + image_filename)
        return
    
    # Get rotation info
    split_rotation = re.search(REGEX, str(split_rotation_value))
    degree = split_rotation.group(1)
    direction = split_rotation.group(2)
    # Negate the degree if the direction is counterclockwise
    if direction == 'CCW':
         degree = '-'+degree
    
    os.system('convert -rotate '+degree+' '+images_source_dir+image_filename+' '+images_target_dir + "/"+image_filename)


# In[5]:


def main():
    # read the metadata
    metadata_df = pd.read_csv(metadata_file, usecols = [image_pid_column_name, rotate_info_column_name], dtype = {image_pid_column_name: "string", rotate_info_column_name: "string"})

    # Create the directory for the result if doesn't exist already
    if not os.path.isdir(images_target_dir):
        os.mkdir(images_target_dir)
     
    # loop through source dir images and rotate them
    print("Being rotating images from " + images_source_dir)
    for image_filename in os.listdir(images_source_dir):
        pid = image_filename.split(".")[0]
        pid = pid.replace("_OBJ", "")
        pid = pid.replace("_", ":")
        rotate_image(image_filename, pid, metadata_df)
    print("Completed rotating images from " + images_source_dir)


# In[ ]:


if __name__ == '__main__':
    main()


# In[ ]:





# In[ ]:




