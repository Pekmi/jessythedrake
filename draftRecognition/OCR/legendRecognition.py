import os
import cv2
import time
import numpy as np
import pytesseract

from windowCapture import get_window_region, capture_screen


# WINDOW_NAME = "League of Legends"
WINDOW_NAME = "draft.png"
TEMPLATE_FOLDER = os.path.join(os.path.dirname(__file__),"championsTemplates")
MIN_MATCHES = 80


def detect_champions(image):
    detected = []

    # Optionnel : convertit en niveaux de gris pour une meilleure précision
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


    # Tu peux aussi ajouter un seuillage ou une amélioration du contraste :
    # gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)

    # OCR config : uniquement lettres majuscules (pour éviter des erreurs)
    config = "--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    text = pytesseract.image_to_string(gray, config=config)
    # print("\nTexte OCR détecté :\n", text)

    # Extraction de mots uniques détectés comme noms
    lines = text.strip().split('\n')
    for line in lines:
        name = line.strip().upper()
        if len(name) >= 3:
            detected.append(name)

    return detected




def segment_image(image):
    """
    Segmente l'image en deux parties (les 30% les plus a gauche et 30% les plus a droite) pour séparer les équipes.
    """
    height, width = image.shape[:2]
    left_img =  image[int(height*0.18):int(height*0.66), int(width*0.1):int(width * 0.24)]
    right_img = image[int(height*0.18):int(height*0.66), int(width*0.8):int(width * 0.9)]
    
    left1, left2, left3, left4, left5      = get_portraits(left_img)
    right1, right2, right3, right4, right5 = get_portraits(right_img)

    left_team = []
    right_team = []
    left_team.append(left1)
    left_team.append(left2)
    left_team.append(left3)
    left_team.append(left4)
    left_team.append(left5)
    right_team.append(right1)
    right_team.append(right2)
    right_team.append(right3)
    right_team.append(right4)
    right_team.append(right5)

    return left_team, right_team


def get_portraits(image):
    """
    Extrait les portraits des champions de l'image.
    """
    height, width = image.shape[:2]

    if width < 5:
        print("Error: Image width is too small to segment into portraits.", end='\r', flush=True)
        time.sleep(.2)
        return None, None, None, None, None
    
    portrait_height = height // 5
    
    portraits = []
    for i in range(5):
        portraits.append(image[i * portrait_height:(i + 1) * portrait_height, :])

    return portraits[0], portraits[1], portraits[2], portraits[3], portraits[4]




if __name__ == "__main__":
    j = True
    while j :
        j = False

        region = get_window_region(WINDOW_NAME)
        if not region:
            continue
    
        screenshot = capture_screen(region)
        if screenshot is None:
            continue

        left_team, right_team = segment_image(screenshot)
        if left_team is None or right_team is None:
            continue
        cv2.imwrite("left_team.png", left_team[0])
        cv2.imwrite("right_team.png", right_team[0])

        left_champions = []
        right_champions = []
        for i in range(5):
            left_champions.append(detect_champions(left_team[i]))
            right_champions.append(detect_champions(right_team[i]))

        print("\n")
        print("Left Team Champions:")
        for champion in left_champions:
            print(champion)
        print("\nRight Team Champions:")
        for champion in right_champions:
            print(champion)