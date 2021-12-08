import cv2
import numpy as np
import pyautogui
import time
import random
from datetime import datetime
import configparser

print("Launching...")

config = configparser.ConfigParser()

config.read('config.ini')

minDelay = int(config['DEFAULT']['MIN_MOUSE_DELAY'])
maxDelay = int(config['DEFAULT']['MAX_MOUSE_DELAY'])
delayDetect = int(config['DEFAULT']['SCREENSHOT_DELAY'])


edgeImg = cv2.imread('images/robotEdge.png')
sliderRight = cv2.imread('images/sliderRight.png')
sliderLeft = cv2.imread('images/sliderLeft.png')
connect = cv2.imread('images/connect.png')
error = cv2.imread('images/error.png')
errorOK = cv2.imread('images/errorOK.png')
sign = cv2.imread('images/metaMaskSignIn.png')
hunt = cv2.imread('images/hunt.png')


pyautogui.FAILSAFE = False
methodList = ['easeInBack', 'easeInBounce', 'easeInCirc', 'easeInCubic', 'easeInElastic', 'easeInExpo', 'easeInOutBack', 'easeInOutBounce', 'easeInOutCirc', 'easeInOutCubic', 'easeInOutElastic', 'easeInOutExpo', 'easeInOutQuad', 'easeInOutQuart','easeInOutQuint', 'easeInOutSine', 'easeInQuad', 'easeInQuart', 'easeInQuint', 'easeInSine', 'easeOutBack', 'easeOutBounce', 'easeOutCirc', 'easeOutCubic', 'easeOutElastic', 'easeOutExpo', 'easeOutQuad', 'easeOutQuart', 'easeOutQuint', 'easeOutSine']


# dragWidth = 1047-897
puzzleWidth = 1125-821  # 304
puzzlePosToSS = 84

edgeSSWidth = 470
edgeSSHight = 370

lower_gray = np.array([0, 0, 110])
upper_gray = np.array([0, 5, 200])

debug = False
testing = False


def randMoveTo(*args):
  randDuration = random.uniform(minDelay, maxDelay)
  evalRandMethod = eval("pyautogui."+random.choice(methodList))
  if len(args) == 1:
    pyautogui.moveTo(args[0][0], args[0][1], randDuration, evalRandMethod)
  else:
    pyautogui.moveTo(args[0], args[1], randDuration, evalRandMethod)


def randMoveRel(*args):
  randDuration = random.uniform(minDelay, maxDelay)
  evalRandMethod = eval("pyautogui."+random.choice(methodList))
  if len(args) == 1:
    pyautogui.moveRel(args[0][0], args[0][1], randDuration, evalRandMethod)
  else:
    pyautogui.moveRel(args[0], args[1], randDuration, evalRandMethod)


def getPosition(template, screenshot, edgeCoords, display=False):
  # take a screenshot as ss
  h, w = template.shape[:-1]

  res = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
  min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
  top_left = max_loc
  bottom_right = (top_left[0] + w, top_left[1] + h)
  center = [edgeCoords.left + top_left[0] +(w/2), edgeCoords.top + top_left[1] + (h/2)]

  if display:
    ss2 = screenshot.copy()
    cv2.rectangle(ss2, top_left, bottom_right, 255, 1)
    cv2.imshow('display pos', ss2)
    cv2.waitKey(0)

  return center


def getProgress(SS):
  hsv = cv2.cvtColor(SS, cv2.COLOR_BGR2HSV)

  mask = cv2.inRange(hsv, lower_gray, upper_gray)

  maskBlur = cv2.medianBlur(mask, 7)

  contours, hierarchy = cv2.findContours(maskBlur, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

  for c in contours:
    if 800 <= cv2.contourArea(c):
      x, y, w, h = cv2.boundingRect(c)
      print("center :", x+(w/2), y+(h/2), "area :",cv2.contourArea(c)) if debug else 0

  if debug:
    cv2.rectangle(SS, (x, y), (x + w, y + h), (0, 255, 0), 1)
    cv2.imshow('puzzle detection', SS)
    cv2.waitKey(0)

  emptyPosToSS = x+(w/2)

  progress = (emptyPosToSS-puzzlePosToSS)/puzzleWidth
  print('progress :', progress) if debug else 0

  return progress

# cv2.imshow('thresh', SS)
# cv2.waitKey(0)


def getDragBarWidth(edgeCoords, SS):
  sliderLeftCoords = getPosition(sliderLeft, SS, edgeCoords)
  print("sliderLeftCoords", sliderLeftCoords) if debug else 0

  randMoveTo(sliderLeftCoords)
  pyautogui.mouseDown()
  randMoveRel(500, 0)

  ssForRight = pyautogui.screenshot(region=(edgeCoords.left, edgeCoords.top, edgeSSWidth, edgeSSHight))
  ssForRight = cv2.cvtColor(np.array(ssForRight), cv2.COLOR_RGB2BGR)

  sliderRightCoords = getPosition(sliderRight, ssForRight, edgeCoords)
  print('rightSideCoords', sliderRightCoords) if debug else 0

  randMoveRel(-580, 0)
  pyautogui.mouseUp()

  dragWidth = sliderRightCoords[0] - sliderLeftCoords[0]
  print("dragWidth", dragWidth) if debug else 0

  return dragWidth, sliderLeftCoords, sliderRightCoords


def finish(sliderLeftCoords, dragTo):
  randMoveTo(sliderLeftCoords)
  pyautogui.mouseDown()
  randMoveRel(dragTo, 0)
  pyautogui.mouseUp()


def solve(edgeCoords):
  SS = pyautogui.screenshot(region=(edgeCoords.left, edgeCoords.top, edgeSSWidth, edgeSSHight))
  SS = cv2.cvtColor(np.array(SS), cv2.COLOR_RGB2BGR)

  progress = getProgress(SS)
  dragBarWidth, sliderLeftCoords, _ = getDragBarWidth(edgeCoords, SS)
  dragTo = progress * dragBarWidth

  if not testing:
    finish(sliderLeftCoords, dragTo)
  else:
    time.sleep(1)

def timeNow():
  return datetime.now().strftime("%H:%M:%S")

def waitFor(image,edge=False,delay=False):
  if delay != False:
    t1 = datetime.now()
  while True:
    try:
      if edge:
        coords = pyautogui.locateOnScreen(image)
      else:
        coords = pyautogui.locateCenterOnScreen(image)
      if coords != None:
        break
      time.sleep(delayDetect)
    except Exception as e:
      print(timeNow(),"ERROR1 :",e)
    if delay != False:
      t2 = datetime.now()
      delta = t2 - t1
      if delta.seconds >= delay:
        return None
  return coords


def main():
  print("Started")
  while True:
    try:
      edgeCoords = pyautogui.locateOnScreen(edgeImg)  # edge
      connectCoords = pyautogui.locateCenterOnScreen(connect) # center
      errorCoords = pyautogui.locateCenterOnScreen(error) # center
      # signCoords = pyautogui.locateCenterOnScreen(sign) # center

      if edgeCoords != None:
        print(timeNow(),"Solving the captcha")
        solve(edgeCoords)
        signCoords = waitFor(sign, delay=10)
        if signCoords != None:
          randMoveTo(signCoords)
          pyautogui.click()

          huntCoords = waitFor(hunt)
          randMoveTo(huntCoords)
          pyautogui.click()

      # elif signCoords != None:
      #   randMoveTo(signCoords)
      #   pyautogui.click()

      elif connectCoords != None:
        print(timeNow(),"Connecting the wallet and launching treasure map")
        randMoveTo(connectCoords)
        pyautogui.click()

        edgeCoords = waitFor(edgeImg,edge=True)
        solve(edgeCoords)

        signCoords = waitFor(sign)
        randMoveTo(signCoords)
        pyautogui.click()

        huntCoords = waitFor(hunt)
        randMoveTo(huntCoords)
        pyautogui.click()

      elif errorCoords != None:
        print(timeNow(),"Detecting an error")
        errorOKCoords = pyautogui.locateCenterOnScreen(errorOK)
        randMoveTo(errorOKCoords)
        pyautogui.click()

      else:
        time.sleep(delayDetect)
        continue

    except Exception as e:
      print(timeNow(),"ERROR :", e)


if __name__ == "__main__":
  main()



# connect = cv2.imread('images/connect.png')
# error = cv2.imread('images/error.png')
# errorOK = cv2.imread('images/errorOK.png')
# sign = cv2.imread('images/metaMaskSignIn.png')
