import pygame
from pygame.locals import *
import pygame.time
import tkinter.filedialog
import tkinter.messagebox
import tkinter.simpledialog

def siglen2tonelen(length_signature: int):
    sigdfour = 48
    return str(length_signature / sigdfour)

def main():
    pygame.init()
    surf = pygame.display.set_mode((800,500), pygame.DOUBLEBUF)
    surf.fill(color=(255, 255, 255))

    songname = "Untitled"
    pygame.display.set_caption("Abarenbou Melody - " + songname)
    songdata = {
        "format": 0,
        "resolution": 48,
        "track": [
            {"position": 0, "category": "property", "length": 0, "type": "initialize"},
            {"position": 0, "category": "property", "length": 0, "type": "tempo", "value": 120},
        ]
    }

    piano_bottomtone = 48
    piano_xpos = 0
    editorsettings = {
        "toneheight": 20,
        "pianowidth": 48,
        "tonewidth": 160,
        "current_length": 24,
        "current_quantize": 12
    }

    draw_pianoroll(surf, piano_bottomtone, piano_xpos, editorsettings, songdata)
    draw_uipanel(surf, piano_xpos, editorsettings, songdata)

    pushedkeys = []

    game_close = 0
    tstamp = 0
    frameclock = pygame.time.Clock()
    while game_close == 0:
        for event in pygame.event.get():
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                pass
            elif event.type == QUIT:
                game_close = 1
            elif event.type == MOUSEBUTTONDOWN:
                if editorsettings["pianowidth"] <= event.pos[0] and editorsettings["toneheight"] * 1 <= event.pos[1] < editorsettings["toneheight"] * 2:
                    mtime = int(((event.pos[0] - editorsettings["pianowidth"]) / editorsettings["tonewidth"] + piano_xpos) * songdata["resolution"] // editorsettings["current_quantize"] * editorsettings["current_quantize"])
                    tfound = None
                    tdelete = None
                    for tcnt, t in enumerate(songdata["track"]):
                        if t["category"] == "property":
                            if t["position"] == mtime:
                                tfound = tcnt
                                if event.button == 3:
                                    tdelete = tfound
                                elif event.button == 1:
                                    if t["type"] == "initialize":
                                        pass
                                    elif t["type"] == "tempo":
                                        #tempoを左クリック
                                        tm = tkinter.simpledialog.askinteger("Abarenbou Melody", "New Tempo(BPM):", initialvalue=t["value"], minvalue=1)
                                        if tm != None:
                                            songdata["track"][tcnt]["value"] = tm                                    
                                    break
                    if tfound == None:
                        ttext = ""
                        while(True):
                            ttext = tkinter.simpledialog.askstring("Abarenbou Melody", "Property Command:", initialvalue=ttext, show="")
                            if ttext == None:
                                ttext = ""
                            if ttext == None or ttext == "":
                                break
                            elif ttext == "i":
                                songdata["track"].append(
                                    {
                                        "position": mtime,
                                        "category": "property",
                                        "length": 0,
                                        "type": "initialize"
                                    }
                                )
                                break
                            elif ttext[0] == "t" and ttext[1:].isdigit():
                                songdata["track"].append(
                                    {
                                        "position": mtime,
                                        "category": "property",
                                        "length": 0,
                                        "type": "tempo",
                                        "value": ttext[1:]
                                    }
                                )
                                break
                    if tdelete != None:
                        del(songdata["track"][tdelete])
                elif editorsettings["toneheight"] * 0 <= event.pos[1] < editorsettings["toneheight"] * 1:
                    #Q、Lの設定
                    if 0 <= event.pos[0] < 240:
                        # Q
                        v = tkinter.simpledialog.askinteger("Abarenbou Melody", "New Quantize Length:", initialvalue=editorsettings["current_quantize"])
                        if v != None:
                            if v > 0:
                                editorsettings["current_quantize"] = v
                    elif 240 <= event.pos[0] < 480:
                        #L
                        v = tkinter.simpledialog.askinteger("Abarenbou Melody", "New Length:", initialvalue=editorsettings["current_length"])
                        if v != None:
                            if v > 0:
                                editorsettings["current_length"] = v
                    pass
                elif event.button == 1:
                    if editorsettings["pianowidth"] <= event.pos[0] and editorsettings["toneheight"] * 2 <= event.pos[1] < surf.get_height() - editorsettings["toneheight"]:
                        # ノート面内
                        print( (event.pos[0] - editorsettings["pianowidth"]) / editorsettings["tonewidth"] + piano_xpos , piano_bottomtone + (surf.get_height() - event.pos[1]) // editorsettings["toneheight"] - 1 )
                        has_dupl = 0
                        for t in songdata["track"]:
                            if t["category"] == "tone":
                                if (
                                    t["position"]
                                    <=
                                    ((event.pos[0] - editorsettings["pianowidth"]) / editorsettings["tonewidth"] + piano_xpos) * songdata["resolution"] // editorsettings["current_quantize"] * editorsettings["current_quantize"]
                                    <
                                    t["position"] + t["length"]
                                    or
                                    t["position"]
                                    <
                                    ((event.pos[0] - editorsettings["pianowidth"]) / editorsettings["tonewidth"] + piano_xpos) * songdata["resolution"] // editorsettings["current_quantize"] * editorsettings["current_quantize"] + editorsettings["current_length"]
                                    <=
                                    t["position"] + t["length"]
                                ):
                                    has_dupl = 1
                        if has_dupl == 0:
                            #noteを配置
                            songdata["track"].append(
                                {
                                    "position": int(((event.pos[0] - editorsettings["pianowidth"]) / editorsettings["tonewidth"] + piano_xpos) * songdata["resolution"] // editorsettings["current_quantize"] * editorsettings["current_quantize"]),
                                    "category": "tone",
                                    "length": editorsettings["current_length"],
                                    "height": piano_bottomtone + (surf.get_height() - event.pos[1]) // editorsettings["toneheight"] - 1
                                }
                            )
                elif event.button == 3:
                    xp = (event.pos[0] - editorsettings["pianowidth"]) / editorsettings["tonewidth"] + piano_xpos
                    yp = piano_bottomtone + (surf.get_height() - event.pos[1]) // editorsettings["toneheight"] - 1
                    deletetone = None
                    for tcnt, t in enumerate(songdata["track"]):
                        if t["category"] == "tone":
                            if (t["position"] <= xp * songdata["resolution"] <= t["position"] + t["length"]) and (t["height"] == yp):
                                deletetone = tcnt
                                print(deletetone)
                    if deletetone != None:
                        del songdata["track"][deletetone]
            elif event.type == KEYDOWN:
#                print("KEYDOWN", event)
                keycode = event.scancode
                if keycode == 79:
                    #RIGHT
#                    piano_xpos = piano_xpos + 0.5
                    pushedkeys.append({"key": 79, "pushdowntime": 0})
                elif keycode == 80:
                    #LEFT
#                    piano_xpos = max(0.0, piano_xpos - 0.5)
                    pushedkeys.append({"key": 80, "pushdowntime": 0})
                elif keycode == 81:
                    #DOWN
#                    piano_bottomtone = max(piano_bottomtone - 1, 0)
                    pushedkeys.append({"key": 81, "pushdowntime": 0})
                elif keycode == 82:
                    #UP
#                    piano_bottomtone = min(piano_bottomtone + 1, 127)
                    pushedkeys.append({"key": 82, "pushdowntime": 0})
                elif keycode == 26:
                    #W
                    editorsettings["current_length"] *= 2
                elif keycode == 22:
                    #S
                    editorsettings["current_length"] //= 2
                elif keycode == 21:
                    #R
                    editorsettings["current_quantize"] *= 2
                elif keycode == 9:
                    #F
                    editorsettings["current_quantize"] //= 2
                elif keycode == 60:
                    #F3 - SAVE
                    sn = export_melody(songname, songdata)
                    if sn != "":
                        songname = sn
                        pygame.display.set_caption("Abarenbou Melody - " + songname)
                elif keycode == 59:
                    #F2 - OPEN
                    istat, idata, sn = import_melody(songname)
                    if istat == 0:
                        songdata = idata
                        songname = sn
                        pygame.display.set_caption("Abarenbou Melody - " + songname)
                elif keycode == 32:
                    #3
                    if editorsettings["current_length"] % 3 == 0 and editorsettings["current_quantize"] % 3 == 0:
                        # 3連符化、3割
                        editorsettings["current_length"] //= 3
                        editorsettings["current_quantize"] //= 3
                    elif editorsettings["current_length"] % 3 != 0 and editorsettings["current_quantize"] % 3 != 0:
                        # もとが3連符。3倍
                        editorsettings["current_length"] *= 3
                        editorsettings["current_quantize"] *= 3
            elif event.type == KEYUP:
                keycode = event.scancode
                if 79 <= keycode <= 82:
                    foundk = None
                    for fcnt, fk in enumerate(pushedkeys):
                        if fk["key"] == keycode:
                            foundk = fcnt
                            break
                    if foundk != None:
                        del(pushedkeys[foundk])
            
            draw_pianoroll(surf, piano_bottomtone, piano_xpos, editorsettings, songdata)
            draw_uipanel(surf, piano_xpos, editorsettings, songdata)
        if pushedkeys != []:
            rd = 0
            for k in pushedkeys:
                if k["pushdowntime"] == 0 or k["pushdowntime"] >= 15:
                    rd = 1
                    if k["key"] == 79:
                        piano_xpos = piano_xpos + 0.5
                    elif k["key"] == 80:
                        piano_xpos = max(0.0, piano_xpos - 0.5)
                    elif k["key"] == 81:
                        piano_bottomtone = max(piano_bottomtone - 1, 0)
                    elif k["key"] == 82:
                        piano_bottomtone = min(piano_bottomtone + 1, 127)
                k["pushdowntime"] += 1
            if rd == 1:
                draw_pianoroll(surf, piano_bottomtone, piano_xpos, editorsettings, songdata)
                draw_uipanel(surf, piano_xpos, editorsettings, songdata)

        pygame.display.flip()
        frameclock.tick(30)
    pygame.quit()

#        surface.fill((255, 0, 0), (0, 0, surface.get_width() // 2, surface.get_height()))

def draw_uipanel(surface, rollposx, editorsettings, song):
    toneheight = editorsettings["toneheight"]
    pianowidth = editorsettings["pianowidth"]
    tonewidth = editorsettings["tonewidth"]

    #top
    pygame.draw.rect(surface, (192, 192, 192), (0, 0, surface.get_width(), toneheight * 2))
    surface.blit(pygame.font.SysFont("monospace", 20).render("Quantize " + str(editorsettings["current_quantize"])+ " (" + siglen2tonelen(editorsettings["current_quantize"]) + ")", False, (0, 0, 0)), (0, 0))
    surface.blit(pygame.font.SysFont("monospace", 20).render("Length " + str(editorsettings["current_length"]) + " (" + siglen2tonelen(editorsettings["current_length"]) + ")", False, (0, 0, 0)), (240, 0))
    rollposxend = (surface.get_width() - pianowidth) / tonewidth + rollposx
    for t in song["track"]:
        if t["category"] == "property":
            if (rollposx <= (t["position"]) / song["resolution"] <= rollposxend):
                surface.blit(
                    pygame.font.SysFont("monospace", 20).render( (t["type"][0] + str(t["value"]) if "value" in t else t["type"][0]), False, (0, 0, 0)),
                    (
                        (float(t["position"]) / song["resolution"] - rollposx) * tonewidth + pianowidth,
                        toneheight
                    )
                )

    #bottom
    pygame.draw.rect(surface, (192, 192, 192), (0, surface.get_height() - toneheight, surface.get_width(), toneheight))
    markposx = pianowidth - (rollposx - int(rollposx)) * tonewidth
    markerx = int(rollposx)
    while markposx <= surface.get_width():
        surface.blit(pygame.font.SysFont("monospace", 20).render(str(markerx), False, (0, 0, 0)), (markposx, surface.get_height() - toneheight))
        pygame.draw.line(surface,       (0, 0, 0), (markposx                  , toneheight * 2), (markposx                  , surface.get_height() - toneheight))
        pygame.draw.line(surface, (192, 192, 192), (markposx + tonewidth * 0.5, toneheight * 2), (markposx + tonewidth * 0.5, surface.get_height() - toneheight))
        markerx += 1
        markposx += tonewidth

def draw_pianoroll(surface, bottomtone, rollposx, editorsettings, song):
    toneheight = editorsettings["toneheight"]
    pianowidth = editorsettings["pianowidth"]
    tonewidth = editorsettings["tonewidth"]
    pygame.draw.rect(surface, (240, 240, 240), (0, 0, surface.get_width(), surface.get_height() - toneheight))
    pianokeytype = [0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0]
    pianocolor = [(240, 240, 240), (16, 16, 16)]

    pygame.draw.rect(surface, (192, 192, 192), (0, surface.get_height() - toneheight, surface.get_width(), toneheight))

    # Notes
    rollposxend = (surface.get_width() - pianowidth) / tonewidth + rollposx
    tonenamelist = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    for t in song["track"]:
        if t["category"] == "tone":
            if (rollposx <= (t["position"]) / song["resolution"] <= rollposxend) or (rollposx <= (t["position"] + t["length"]) / song["resolution"] <= rollposxend):
                pygame.draw.rect(
                    surface,
                    (192, 192, 64),
                    (
                        (float(t["position"]) / song["resolution"] - rollposx) * tonewidth + pianowidth, 
                        (bottomtone - t["height"]) * toneheight + surface.get_height() - toneheight * 2 + 1,
                        (float(t["length"]) / song["resolution"]) * tonewidth - 2,
                        toneheight - 1
                    )
                )
                surface.blit(
                    pygame.font.SysFont("monospace", 20).render(tonenamelist[t["height"] % 12] + str(t["height"] // 12), False, (0, 0, 0)),
                    (
                        (float(t["position"]) / song["resolution"] - rollposx) * tonewidth + pianowidth,
                        (bottomtone - t["height"]) * toneheight + surface.get_height() - toneheight * 2
                    )
                )
                

    #Grid & Piano Tiles
    for ycnt in range((surface.get_height() - toneheight) // toneheight + 1):
        pygame.draw.rect(
            surface,
            pianocolor[pianokeytype[(bottomtone + ycnt) % 12]], 
            (0, surface.get_height() - toneheight * (ycnt + 2), pianowidth * 2 / 3, toneheight)
        )
        pygame.draw.rect(
            surface,
            pianocolor[0], 
            (pianowidth * 2 / 3, surface.get_height() - toneheight * (ycnt + 2), pianowidth * 1 / 3, toneheight)
        )
        if (bottomtone + ycnt) % 12 == 0:
            surface.blit(pygame.font.SysFont("monospace", 20).render("C" + str((bottomtone + ycnt) // 12), False, (0, 0, 0)), (0, surface.get_height() - toneheight * (ycnt + 2)) )
        pygame.draw.line(
            surface,
            (128, 128, 128),
            (0                  , surface.get_height() - toneheight * (ycnt + 1)),
            (surface.get_width(), surface.get_height() - toneheight * (ycnt + 1)),
            1 if ((bottomtone + ycnt) % 12 != 0) else 2
        )
    pygame.draw.line(
        surface,
        (128, 128, 128),
        (pianowidth, toneheight * 2),
        (pianowidth, surface.get_height()),
        2
    )
    #events
    pygame.draw.rect(surface, (192, 192, 192), (0, toneheight, surface.get_width(), toneheight))

def export_melody(filename, song):
    tonenamelist = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    
    res = song["resolution"]
    song["track"].sort(key=lambda x: x["position"])
    exportdata = ""
    tstamp = 0
    errorcode = 0
    octave = 0
    currentlength = 48
    tempo = 120
    for t in song["track"]:
        if tstamp > t["position"]:
            errorcode = 1
            break
        if tstamp < t["position"]:
            #Restを挿入する
            if t["position"] - tstamp != currentlength:
                exportdata += "L" + str(t["position"] - tstamp) + " "
                currentlength = t["position"] - tstamp
            exportdata += "R "
            tstamp += t["position"] - tstamp
        if t["category"] == "tone":
            if t["length"] != currentlength:
                exportdata += "L" + str(t["length"]) + " "
                currentlength = t["length"]
            toct = (t["height"] + 3) // 12 - 4
            if toct != octave:
                if toct - octave > 0:
                    #オクターブを上げる
                    exportdata += ("^" * (toct - octave))
                if toct - octave < 0:
                    #オクターブを下げる
                    exportdata += ("v" * (octave - toct))
                octave = toct
            exportdata += tonenamelist[t["height"] % 12] + " "
            tstamp += t["length"]
        elif t["category"] == "property":
            if t["type"] == "initialize":
                exportdata += "i "
                octave = 0
                currentlength = 48
                tempo = 120
            elif t["type"] == "tempo":
                exportdata += "T" + str(t["value"]) + " "
    if errorcode != 0:
        tkinter.messagebox.showerror("Abarenbou Melody", "Export failed with code " + str(errorcode))
        print("E: export failed with code ", errorcode)
        print(exportdata)
        fn = ""
    else:
        fn = tkinter.filedialog.asksaveasfilename(filetypes=[("melody", "txt")])
        if fn != "":
            with open(fn, mode="w") as f:
                f.write(exportdata)
    return fn

def import_melody(filename):
    importstat = -1
    fn = tkinter.filedialog.askopenfilename(filetypes=[("melody", "txt")])
    rawmelody = ""
    if fn != "":
        importstat = 0
        with open(fn, mode="r") as f:
            rawmelody = f.read()
    importdata = {
        "format": 0,
        "resolution": 48,
        "track":[]
    }
    i = 0
    time = 0
    tempo = 120
    length = 48
    octave = 0
    tonechars = "ABCDEFG"
    toneheights = [-3, -1, 0, 2, 4, 5, 7]
    lasttonetype = "Rest"
    while(i < len(rawmelody)):
        if rawmelody[i].isspace():
            i += 1
            continue
        elif rawmelody[i] == 'i':
            importdata["track"].append({"position": time, "category": "property", "length": 0, "type": "initialize"})
            tempo = 120
            length = 48
            octave = 0
            i += 1
        elif rawmelody[i] == 'T':
            i += 1
            v = 0
            while(rawmelody[i].isdigit()):
                v = v * 10 + int(rawmelody[i])
                i += 1
            importdata["track"].append({"position": time, "category": "property", "length": 0, "type": "tempo", "value": v})
        elif rawmelody[i] == 'L':
            i += 1
            v = 0
            while(rawmelody[i].isdigit()):
                v = v * 10 + int(rawmelody[i])
                i += 1
            length = v
        elif rawmelody[i] == '^':
            octave += 1
            i += 1
        elif rawmelody[i] == 'v':
            octave -= 1
            i += 1
        elif rawmelody[i] in tonechars:
            lasttonetype = "Tone"
            th = toneheights[tonechars.find(rawmelody[i])] + (octave + 4) * 12
            i += 1
            if rawmelody[i] == '#':
                th += 1
                i += 1
            elif rawmelody[i] == 'b':
                th -= 1
                i += 1
            importdata["track"].append({"position": time, "category": "tone", "length": length, "height": th})
            time += length
        elif rawmelody[i] == 'R':
            lasttonetype = "Rest"
            i += 1
            time += length
        elif rawmelody[i] == '-':
            #print(lasttonetype)
            if lasttonetype == "Rest":
                time += length
                i += 1
            elif lasttonetype == "Tone":
                hi = -1
                while(importdata["track"][hi]["category"] != "tone"):
                    hi -= 1
                    if -hi >= len(importdata["track"]):
                        hi = None
                        break
                #print(hi)
                if hi != None:
                    importdata["track"][hi]["length"] += length
                i += 1
                time += length
        else:
            i += 1
    
    #print(importdata)
    return importstat, importdata, fn

if __name__ == "__main__":
    main()