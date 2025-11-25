import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

DirRV=17
PwmRV=27
GPIO.setup(PwmRV,GPIO.OUT)
GPIO.setup(DirRV,GPIO.OUT)
rv=GPIO.PWM(PwmRV,100)

DirR=22
PwmR=10
GPIO.setup(DirR,GPIO.OUT)
GPIO.setup(PwmR,GPIO.OUT)
r=GPIO.PWM(PwmR,100)

DirL=9
PwmL=11
GPIO.setup(DirL,GPIO.OUT)
GPIO.setup(PwmL,GPIO.OUT)
l=GPIO.PWM(PwmL,100)

DirLV=5
PwmLV=6
GPIO.setup(DirLV,GPIO.OUT)
GPIO.setup(PwmLV,GPIO.OUT)
lv=GPIO.PWM(PwmLV,100)

rv.start(0)
r.start(0)
l.start(0)
lv.start(0)


def RV(w):
    if(w<=0):
        GPIO.output(DirRV,GPIO.HIGH)
        rv.ChangeDutyCycle(abs(w))
    if(w>0):
        GPIO.output(DirRV,GPIO.LOW)
        rv.ChangeDutyCycle(abs(w))

def R(x):
    if(x<=0):
        GPIO.output(DirR,GPIO.HIGH)
        r.ChangeDutyCycle(abs(x))
    if(x>0):
        GPIO.output(DirR,GPIO.LOW)
        r.ChangeDutyCycle(abs(x))

def L(y):
    if(y>=0):
        GPIO.output(DirL,GPIO.HIGH)
        l.ChangeDutyCycle(abs(y))
    if(y<0):
        GPIO.output(DirL,GPIO.LOW)
        l.ChangeDutyCycle(abs(y))
def LV(z):
    if(z<=0):
        GPIO.output(DirLV,GPIO.HIGH)
        lv.ChangeDutyCycle(abs(z))
    if(z>0):
        GPIO.output(DirLV,GPIO.LOW)
        lv.ChangeDutyCycle(abs(z))
        
        
