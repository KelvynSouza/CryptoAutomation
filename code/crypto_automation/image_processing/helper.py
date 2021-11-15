import cv2
import numpy as np
from matplotlib import pyplot as plt

class ImageHelper:
    def find_exact_match_position(self, image, template):
        method = cv2.TM_SQDIFF_NORMED

        result = cv2.matchTemplate(image, template, method)

        # We want the minimum squared difference, because of the TM_SQDIFF_NORMED
        mn,_,mnLoc,_ = cv2.minMaxLoc(result)

        # Extract the coordinates of our best match
        MPx,MPy = mnLoc

        # Step 2: Get the size of the template. This is the same size as the match.
        trows,tcols = template.shape[:2]

        x_final_position = MPx+tcols

        y_final_position = MPy+trows

        #only use match with great confidence, we use threshold 0.1 because 
        #with TM_SQDIFF_NORMED the nearer to 0 the better matched
        threshold = 0.05
        loc = np.where(result <= threshold)

        #if it doesnt match anything, it will be 0
        matches = list(zip(*loc[::-1]))

        if matches:
            center_position = type('',(object,),{"x": 0, "y":0})()
            center_position.x = round(((MPx + x_final_position) / 2))
            center_position.y = round(((MPy + y_final_position) / 2))
            return center_position
        else: 
            return None
    

    #region util 
    def show_info(image, isgray=False):
        print('-----------------------------------------------------')    
        print('shape:', image.shape, 'and', 'size:', image.size)    
        print(image.dtype)

        if isgray:
            plt.imshow(image, cmap='gray')        
        else:
            plt.imshow(image[:,:,::-1])

        plt.show()
        #endregion