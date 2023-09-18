import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
import time
import random
from flask import Flask, render_template, Response,request

app = Flask(__name__)

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

detector = HandDetector(maxHands=1)

timer = 0
stateResult = False
startGame = False
scores = [0, 0]

@app.route('/')
def index():
    return render_template('index.html')

def generate_frames():
    global timer, stateResult, startGame, scores

    while True:
        back_img = cv2.imread("static/BG.png")
        success, img = cap.read()

        img_scaled = cv2.resize(img, (0, 0), None, 0.875, 0.875)
        img_scaled = img_scaled[:, 80:480]

        hands, img = detector.findHands(img_scaled)

        if startGame:

            if stateResult is False:
                timer = time.time() - initialTime
                cv2.putText(back_img,str(int(timer)),(605,435),cv2.FONT_HERSHEY_PLAIN,6,(255,0,255),4)

                if timer > 3:
                    stateResult = True
                    timer = 0

                    if hands:
                        playerMove = None
                        hand = hands[0]
                        fingers = detector.fingersUp(hand)

                        if fingers == [0, 0, 0, 0, 0]:
                            playerMove = 1

                        if fingers == [1, 1, 1, 1, 1]:
                            playerMove = 2

                        if fingers == [0, 1, 1, 0, 0]:
                            playerMove = 3

                        rand_no = random.randint(1, 3)

                        imgAI = cv2.imread(f'static/{rand_no}.png', cv2.IMREAD_UNCHANGED)
                        back_img = cvzone.overlayPNG(back_img, imgAI, (149, 310))

                        # player wins
                        if (playerMove == 1 and rand_no == 3) or \
                           (playerMove == 2 and rand_no == 1) or \
                           (playerMove == 3 and rand_no == 2):
                            print("player won")
                            scores[1] += 1

                        # ai wins
                        if (playerMove == 3 and rand_no == 1) or \
                           (playerMove == 1 and rand_no == 2) or \
                           (playerMove == 2 and rand_no == 3):
                            print("ai won")
                            scores[0] += 1

        back_img[234:654, 795:1195] = img_scaled
        if stateResult:
            back_img = cvzone.overlayPNG(back_img, imgAI, (149, 310))

        cv2.putText(back_img, str(scores[0]), (410, 215), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)
        cv2.putText(back_img, str(scores[1]), (1112, 215), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)

        _, buffer = cv2.imencode('.jpg', back_img)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_game', methods=['POST'])
def start_game():
    global initialTime, startGame, stateResult

    if request.method == 'POST':
        initialTime = time.time()
        startGame = True
        stateResult = False

    return '', 204  # Return a successful response with no content

if __name__ == "__main__":
    app.run(debug=True)
