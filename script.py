from PIL import Image, ImageOps, ImageGrab
import threading, time

def analyze():
    screenshot = ImageGrab.grab()
    im = screenshot.crop(rect)
    im = im.convert("L")
    im.save('test992.png')
    W, H = im.size
    pix = im.load()
    
    fond = pix[0,0] #pix[abs,ord]
    #print(fond)
    
    if fond < 128: #La couleur du fond est foncée
        im = ImageOps.invert(im) #On inverse l'image
        pix = im.load()
        fond = pix[0,0]
        #print("Image négativée")
    
    BOXES = []
    gauche = 0
    droite = 0
    bas = 0
    haut = H
    for w in range(W):
        found = False
        for h in range(H):
            if not pix[w, h] or fond/pix[w, h] > 1.4 : #pixel noir trouvé
                found = True
                if not gauche:
                    gauche = w
                if w >= droite:
                    droite = w+1
                    
                if h < haut:
                    haut = h
                if h >= bas:
                    bas = h+1
    
        if not found and gauche: #fin du chiffre
            BOXES.append((gauche, haut, droite, bas))
            gauche = 0
            droite = 0
            bas = 0
            haut = H
            
    #print(len(BOXES), "chiffres trouvés")
    
    for i, box in enumerate(BOXES):
        chiffre = im.crop(box)
        chiffre.save(str(i)+'.png')
    
    def vertical(i, chiffre, pix): #Déterminer où sont les pixels sur la ligne verticale
        '''
        0. En haut et en bas
        1. Au dessus du milieu
        2. En haut, en dessous du milieu (mais pas en bas) ou au milieu et en bas */***
        3. En haut, au milieu et en bas *
        4. Au dessus du milieu (mais pas en haut), en dessous du milieu (mais pas en bas)
        5. En haut, au milieu et en bas *
        6. En haut (ou proche), au milieu et en bas *
        7. En haut, milieu (ou proche)
        8. En haut, au milieu et en bas *
        9. En haut, en dessous du milieu (mais pas en bas) x 2 ou en bas */***
        '''
        W, H = chiffre.size
        milieu_w = int(W/2)
        found = False
        hauteurs = []
        for h in range(H):
            if not pix[milieu_w, h] or  fond/pix[milieu_w, h] > 1.4:
                if not found: #pixel noir trouvé
                    found = True
                    hauteurs.append(h)
            elif found:
                found = False

        if len(hauteurs) == 1: #1
            #print(i,"is a 1")
            return 1
        
        elif len(hauteurs) == 2: #0 4 7
            if hauteurs[0] == 0: #0 7
                return tiers_sup(i, W, H, milieu_w, pix, (0,7))
            else:
                #print(i,"is a 4")
                return 4
    
        elif len(hauteurs) == 3: #2 3 5 6 8 9    
            return tiers_sup(i, W, H, milieu_w, pix)
    
    
    def tiers_sup(i, W, H, milieu_w, pix, d=None): #(*) Distinguer les 0, 7, 2, 3, 5, 6, 8, 9 partiellement 
        '''
        0. A gauche et à droite **
        7. A droite **
        2. A droite **
        3. A droite **
        5. A gauche **
        6. A gauche **   
        8. A gauche et à droite **
        9. A gauche et à droite **
        '''
        first_tiers_h = int(H/3)
        found = False
        largeurs = []
        for w in range(W):
            if not pix[w, first_tiers_h] or fond/pix[w, first_tiers_h] > 1.4:
                if not found: #pixel noir trouvé
                    found = True
                    largeurs.append(w)
            elif found:
                found = False
                
        if d == (0,7):#0 7
            if len(largeurs) == 1: #7
                return 7
            elif len(largeurs) == 2: #0
                return 0

        if len(largeurs) == 1: #2 3 5 6
            if largeurs[0] > milieu_w: #2 3 (A droite)
                return tiers_inf(i, W, H, milieu_w, pix, (2,3))
    
            else: #5 6 (A gauche)
                return tiers_inf(i, W, H, milieu_w, pix, (5,6))
        
        elif len(largeurs) == 2: #8 9
            return tiers_inf(i, W, H, milieu_w, pix, (8,9))
        
        
    
    def tiers_inf(i, W, H, milieu_w, pix, d): #(**) Distinguer le 2 du 3 et le 5 du 6 et le 8 du 9
        '''
        2. Au milieu
        3. A droite
        5. A droite
        6. A gauche et à droite
        8. A gauche et à droite
        9. A droite
        '''
        snd_tiers_h = int(H*2/3)
                
        if d == (2,3):
            for w in range(W-1,-1,-1): #On commence par la droite
                if not pix[w, snd_tiers_h] or fond/pix[w, snd_tiers_h] > 1.4:
                    if w >= W-(milieu_w/2): #3
                        #print(i, "is a 3")
                        return 3
                    else: #2
                        #print(i, "is a 2")
                        return 2
                    break
                
        elif d == (5,6):
            largeurs = []
            found = False
            for w in range(W):
                if not pix[w, snd_tiers_h] or fond/pix[w, snd_tiers_h] > 1.4:
                    if not found: #pixel noir trouvé
                        found = True
                        largeurs.append(w)
                elif found:
                    found = False
    
            if len(largeurs) == 1: #5
                #print(i, "is a 5")
                return 5
            else: #6
                #print(i, "is a 6")
                return 6
    
        elif d == (8,9):
            largeurs = []
            found = False
            for w in range(W):
                if not pix[w, snd_tiers_h] or fond/pix[w, snd_tiers_h] > 1.4:
                    if not found: #pixel noir trouvé
                        found = True
                        largeurs.append(w)
                elif found:
                    found = False
    
            if len(largeurs) == 1: #9
                #print(i, "is a 9")
                return 9
            else: #8
                #print(i, "is a 8")
                return 8
                
            
    result = []      
    for i, box in enumerate(BOXES):
        chiffre = im.crop(box)
        pix = chiffre.load()
        result.append(vertical(i, chiffre, pix))
    
    print('RESULTAT :', ''.join(str(_) for _ in result))

x0, y0, x1, y1 = 0, 0, 0, 0
def start(event):
    global FRAME, x0, y0, top, st, count
    x0, y0 = event.x, event.y
    count = 0
    st = 0
    try:
        FRAME.destroy()
    except:
        pass
    try:
        top.destroy()
    except:
        pass

    FRAME = tk.Frame(root, width = 20, height = 20, bg = 'white')
    root.event_generate("<Motion>", warp=True, x=x0+20, y=y0+20)
    FRAME.place(x=x0,y=y0)


def draw(event):
    global FRAME, label_started
    x, y = event.x, event.y
    FRAME.configure(width=abs(x0-x), height=abs(y0-y))

def release(event):
    global FRAME, x1, y1, top, button
    x1, y1 = event.x, event.y
    top = tk.Toplevel(root)    
    top.attributes('-alpha', 1)
    top.wm_attributes("-topmost", True)
    top.overrideredirect(True)
    button = ttk.Button(top, text='START')
    button.bind('<ButtonRelease-1>', button_release)
    button.pack()
    top.geometry(f"{button.winfo_reqwidth()}x{button.winfo_reqheight()}+{x1+5}+{y1}")
    #FRAME.destroy()
    
def leave(event):
    root.wm_state('iconic')
    
st = 0
def button_release(event):
    global rect, st
    rect = (x0, y0, x1, y1)
    top.destroy()
    FRAME.destroy()
    root.wm_state('iconic')
    #st = time.time()
    threading.Thread(target=boucle, daemon=True).start()

count = 0
def boucle():
    global count
    analyze()
    count+=1
    #if count == 30:
    #    print(time.time()-st, f'secondes pour faire {count} recherches')
    #    return
    boucle()

import tkinter as tk
import tkinter.ttk as ttk

root = tk.Tk()
root.geometry("1920x1080+0+0")
#root.lift()
root.wm_attributes("-topmost", True)
root.attributes('-fullscreen', True)
root.configure(background='blue2')
root.attributes("-transparentcolor", "white")
root.attributes('-alpha', 0.30)
root.config(cursor="cross")
root.bind('<ButtonPress-1>', start)
root.bind('<B1-Motion>', draw)
root.bind('<ButtonRelease-1>', release)
root.bind('<Escape>', leave)
root.mainloop()
