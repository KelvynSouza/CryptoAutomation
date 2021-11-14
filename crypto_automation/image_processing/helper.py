import cv2
import numpy as np
from matplotlib import pyplot as plt
from scipy.signal import fftconvolve


def find_in_image(image, template):
    #Esta é a normalização e correlação entre a imagem e o template,
    #Quando a função da o "match" da imagem com o template 
    #Vc vera o lugar com uma Luz branca chamativa na imagem, 
    #este é o local onde ele achou a imagem que ele buscava
    result = __normxcorr2(template, image, "same")

    location = np.where(result==result.max())

    y_value = (location[0])[0]
    x_value = (location[1])[0]

    #circulei a luz branca maior que citei mais em cima
    cv2.circle(result, (x_value, y_value), 60, (255, 0, 0), 2)
    __show_info(result)

    cv2.circle(image, (x_value, y_value), 60, (255, 0, 0), 2)
    __show_info(image)


def find_exact_match_position(image, template):
    method = cv2.TM_SQDIFF_NORMED

    result = cv2.matchTemplate(image, template, method)

    # We want the minimum squared difference
    mn,_,mnLoc,_ = cv2.minMaxLoc(result)

    # Draw the rectangle:
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
        center_position = (round(((MPx + x_final_position) / 2)), round(((MPy + y_final_position) / 2)))
        return center_position
    else: 
        return None

#region util 
def __show_info(image, isgray=False):
    print('-----------------------------------------------------')    
    print('shape:', image.shape, 'and', 'size:', image.size)    
    print(image.dtype)
    
    if isgray:
        plt.imshow(image, cmap='gray')        
    else:
        plt.imshow(image[:,:,::-1])
     
    plt.show()

def __normxcorr2(template, image, mode="full"):
    """
    Input arrays should be floating point numbers.
    :param template: N-D array, of template or filter you are using for cross-correlation.
    Must be less or equal dimensions to image.
    Length of each dimension must be less than length of image.
    :param image: N-D array
    :param mode: Options, "full", "valid", "same"
    full (Default): The output of fftconvolve is the full discrete linear convolution of the inputs. 
    Output size will be image size + 1/2 template size in each dimension.
    valid: The output consists only of those elements that do not rely on the zero-padding.
    same: The output is the same size as image, centered with respect to the ‘full’ output.
    :return: N-D array of same dimensions as image. Size depends on mode parameter.
    """

    # If this happens, it is probably a mistake
    if np.ndim(template) > np.ndim(image) or \
            len([i for i in range(np.ndim(template)) if template.shape[i] > image.shape[i]]) > 0:
        print("normxcorr2: TEMPLATE larger than IMG. Arguments may be swapped.")

    template = template - np.mean(template)
    image = image - np.mean(image)

    a1 = np.ones(template.shape)
    # Faster to flip up down and left right then use fftconvolve instead of scipy's correlate
    ar = np.flipud(np.fliplr(template))
    out = fftconvolve(image, ar.conj(), mode=mode)
    
    image = fftconvolve(np.square(image), a1, mode=mode) - \
            np.square(fftconvolve(image, a1, mode=mode)) / (np.prod(template.shape))

    # Remove small machine precision errors after subtraction
    image[np.where(image < 0)] = 0

    template = np.sum(np.square(template))
    out = out / np.sqrt(image * template)

    # Remove any divisions by 0 or very close to 0
    out[np.where(np.logical_not(np.isfinite(out)))] = 0
    
    return out
#endregion

path_image_test = '../images/test/login_page_wrong.png'
path_image_template = '../images/connect_wallet.png'

img = cv2.imread(path_image_test)
template = cv2.imread(path_image_template)

match_position = find_exact_match_position(img, template)

if match_position:
    cv2.circle(img, (x_position, y_position), 10, (0,0,255), 2)
__show_info(img)