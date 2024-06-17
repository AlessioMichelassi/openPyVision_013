import cv2
import numpy as np

# Carica l'immagine
image1 = cv2.imread(r"C:\Users\aless\Pictures\len_full.jpg")


def bitwise_screen(image1, times=5):
    result = image1
    for _ in range(times):
        # Inverti l'immagine
        not_image = cv2.bitwise_not(result)
        # AND inversi
        and_result = cv2.bitwise_and(not_image, not_image)
        # Inverti di nuovo per ottenere l'effetto screen
        result = cv2.bitwise_not(and_result)
    return result


def normalScreen(image1):
    image = image1 / 255.0
    screen_result = 1 - (1 - image) * (1 - image)
    screen_result = (screen_result * 255).astype(np.uint8)
    return screen_result


def fast_screenOLD(image1, difference=0.0):
    opacity = 0.5 - difference
    not_image = cv2.bitwise_not(image1)
    screen_result = cv2.addWeighted(not_image, opacity, not_image, opacity, 0)
    return cv2.bitwise_not(screen_result)

def fast_screen(image1, difference=0.0):
    not_image = cv2.bitwise_not(image1)
    # Scale not_image to simulate (1 - A) * (1 - B)
    screen_result = 255 - cv2.multiply(not_image, not_image, scale=1.0 / 255.0)
    return screen_result


# Calcola la luminosità media
def calculate_brightness(image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return np.mean(gray_image)


# Esegui l'operazione di screen
screen_result = bitwise_screen(image1, 10)
fast_screen_result = fast_screen(image1, 0)
fast_screen_result2 = fast_screen(image1, 0.12)
normalScreen_result = normalScreen(image1)

# Calcola la luminosità media dell'immagine originale e di quella elaborata
original_brightness = calculate_brightness(image1)
screen_brightness = calculate_brightness(screen_result)
fast_screen_brightness = calculate_brightness(fast_screen_result)
fast_screen_result2_brightness = calculate_brightness(fast_screen_result2)
normalScreen_brightness = calculate_brightness(normalScreen_result)

# Stampa i risultati
print('Original brightness:', original_brightness)
print('Screen brightness:', screen_brightness)
print('Fast Screen brightness:', fast_screen_brightness)
print('Fast Screen 2 brightness:', fast_screen_result2_brightness)
print('Normal Screen brightness:', normalScreen_brightness)

# Mostra i risultati
cv2.imshow('Original', image1)
cv2.imshow('Screen Result', screen_result)
cv2.imshow('Fast Screen Result', fast_screen_result)
cv2.imshow('Fast Screen Result 2', fast_screen_result2)
cv2.imshow('Normal Screen Result', normalScreen_result)
cv2.waitKey(0)
