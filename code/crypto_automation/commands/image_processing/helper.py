import cv2
import time
import numpy as np
from matplotlib import pyplot as plt

class ImageHelper:
    def __find_exact_match_position(self, image, template, should_grayscale = True, confidence_level = 0.1):
        method = cv2.TM_SQDIFF_NORMED

        if should_grayscale:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            template = cv2.cvtColor(template, cv2.COLOR_RGB2GRAY)

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
        threshold = confidence_level
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


    def __find_exact_matches_position(self, image, template, should_grayscale = True, confidence_level = 0.1):
        method = cv2.TM_SQDIFF_NORMED

        if should_grayscale:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            template = cv2.cvtColor(template, cv2.COLOR_RGB2GRAY)

        result = cv2.matchTemplate(image, template, method)

        mn,_,mnLoc,_ = cv2.minMaxLoc(result)

        MPx,MPy = mnLoc

        template_y, template_x = template.shape[:2]

        threshold = confidence_level
        loc = np.where(result <= threshold)

        matches = list(zip(*loc[::-1]))

        points = []        
        if matches:
            rectangles = []
            for loc in matches:
                rect = [int(loc[0]), int(loc[1]), template_x, template_y]

                rectangles.append(rect)
                rectangles.append(rect)

            rectangles, weights = cv2.groupRectangles(rectangles, groupThreshold=1, eps=0.5)  
            
            if len(rectangles):
                for (x, y, w, h) in rectangles:
                    center_x = x + int(w/2)
                    center_y = y + int(h/2)
                    points.append((center_x, center_y))
            
        return points


    def wait_until_match_is_found(self, method_image_to_validate, method_image_to_validate_args, template_path, timeout, confidence_level = 0.1, should_throw_exception = False, should_grayscale = True): 
        duration = 0
        result = None        
        template = cv2.imread(template_path)    

        while result == None and duration < timeout:
            time.sleep(1)
            duration += 1
            website_picture = method_image_to_validate(*method_image_to_validate_args) 
            result = self.__find_exact_match_position(website_picture, template, should_grayscale, confidence_level)  

        if result == None and should_throw_exception == True:
            raise Exception(f"Element {template_path} not found on screen!")

        return result


    def wait_all_until_match_is_found(self, method_image_to_validate, method_image_to_validate_args, template_path, timeout, confidence_level = 0.1, should_throw_exception = False, should_grayscale = True): 
        duration = 0
        result = None        
        template = cv2.imread(template_path)    

        while result == None and duration < timeout:
            time.sleep(1)
            duration += 1
            website_picture = method_image_to_validate(*method_image_to_validate_args) 
            result = self.__find_exact_matches_position(website_picture, template, should_grayscale, confidence_level)  

        if result == None and should_throw_exception == True:
            raise Exception(f"Element {template_path} not found on screen!")

        return result

    
    def show_image(image, isgray=False):
        print('-----------------------------------------------------')    
        print('shape:', image.shape, 'and', 'size:', image.size)    
        print(image.dtype)

        if isgray:
            plt.imshow(image, cmap='gray')        
        else:
            plt.imshow(image[:,:,::-1])

        plt.show()
    

    def rescale_frame(self, frame, percent=30, convert_grayscale=False):
        width = int(frame.shape[1] * percent/ 100)
        height = int(frame.shape[0] * percent/ 100)
        dim = (width, height)        
        return cv2.resize(frame, dim, interpolation = cv2.INTER_LANCZOS4)
