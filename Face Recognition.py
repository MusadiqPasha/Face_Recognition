import face_recognition
import numpy as np
from datetime import datetime
import os
import cv2
import keyboard
import pyautogui
import customtkinter as cstk
import tkinter as tk
from tkinter import filedialog, PhotoImage

path = "ImagesAttendance"
only_name = r"only_name"
attend_csv_path = r"Attendance.csv"
# GUIIIII
cstk.set_appearance_mode("dark")
cstk.set_default_color_theme("green")
root = cstk.CTk()
root.geometry("1920x1080")
root.title("Facial Recognition System")

# create the needed variables

images = []  #  img to numpy array
global image_names
global filesz
global encodeList
encodeList=[]
filesz=tuple()
image_names = []  # stores people's namesz
mylist = os.listdir(path)  # lists all the images in dir
savedImg = []
global attend_dict
attend_dict={}
print(mylist)
global del_names,del_ind
del_names=[]
del_ind=[]
# accessing images in folder


def access():
    global images,image_names
    for cl in mylist:
        curImg = cv2.imread(f'{path}/{cl}')
        images.append(curImg)
        image_names.append(os.path.splitext(cl)[0]) #root path of name [0] ext path [1]
    print(image_names)
    image_names2 = image_names[:]


def clean():
    for f in os.listdir(only_name):
        os.remove(fr"{only_name}\{f}")


# return the 128-dimension face encoding for each face in the image.
# A face encoding is basically a way to represent the face using a set of 128 computer-generated measurements.
# Two different pictures of the same person would have similar encoding and
# two different people would have totally different encoding


def find_encodings(images):
    for image in images:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(image)[0]
        encodeList.append(encode)
    return encodeList


# to save the captured image
def save_img(imagesz,nami):
    savedImg=os.listdir(only_name)
    if nami not in savedImg:
        cv2.imwrite(rf"{only_name}+\{nami}.jpg", imagesz)


# to mark the attendace into txt file for a new name
def markAttendance(name):
    print(name, "attended")

    with open("Attendance.csv", 'r+') as f:
        myDataList = f.readlines()  # reads every line in attendance list

        for line in myDataList:
            line = line.strip()
            entry = line.split(',')
            attend_dict[entry[0]] = entry[1:]

        if name not in attend_dict.keys():
            now = datetime.now()
            dtString = now.strftime("%I:%M %p")  # I - 12 hr format() , minute , pm or am
            attend_dict[name] = [dtString,""]  # writes time

        elif name in attend_dict.keys():
            now = datetime.now()
            dtString = now.strftime("%I:%M %p")  # I - 12 hr format() , minute , pm or am
            attend_dict[name][1]=dtString


def webcam_scan():
    cap = cv2.VideoCapture(0) # starts video capture through webcam

    while True:
        # img = numpy array  ,  succces= if loaded or not
        success,img = cap.read()
        # we resizze to 1/4th of size of ease of calculation and faster read time
        imgS = cv2.resize(img,(0,0),None,0.25,0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        # no of faces in an frame
        facesCurFrame = face_recognition.face_locations(imgS)
        encodesCurFrame = face_recognition.face_encodings(imgS,facesCurFrame)

        # displays a text below                         no               co ordi where tot          font                colour    size
        cv2.putText(img,f'Number of faces detected: {len(facesCurFrame)}', (100, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 255), 2)

        # main shittt
        for encodeFace,FaceLoc in zip(encodesCurFrame,facesCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown,encodeFace,tolerance=0.5) # lower is more strict
            faceDis = face_recognition.face_distance(encodeListKnown,encodeFace)
            matchIndex = np.argmin(faceDis) # gives matchIndex of match name out of all images
            if matches[matchIndex]:
                name = image_names[matchIndex].upper() # Capitalizes each word
                # print(name)
                # FaceLoc = up right down left
                y1,x2,y2,x1=FaceLoc
                # multiply by 4 cuz we decresed the size by 4
                # were drwaing on regular image not of reduced size one
                y1, x2, y2, x1=y1*4,x2*4,y2*4,x1*4

                # draw's rectangle img , loc , colour , size
                cv2.rectangle(img, (x1,y1),(x2,y2) ,(255, 255, 0), 2)
                cv2.rectangle(img, (x1, y2-35), (x2, y2),(255, 255, 0), cv2.FILLED)
                # displays name
                cv2.putText(img,name,(x1+6,y2-6),cv2.FONT_HERSHEY_COMPLEX,1,(0,255,255),2)
                # save img
                save_img(img, name)

                # call's attendace to add name
                markAttendance(name)

            else:
                    name = "UNKNOWN"
                    # FaceLoc = up right down left
                    y1, x2, y2, x1 = FaceLoc
                    # multiply by 4 cuz we decresed the size by 4
                    # were drwaing on regular image not of reduced size one
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4

                    # draw's rectangle img , loc , colour , size
                    cv2.rectangle(img, (x1, y1), (x2, y2), (255, 255, 0), 2)
                    cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (255, 255, 0), cv2.FILLED)
                    # displays name
                    cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 255), 2)

        # continouly displays the image
        cv2.imshow('webcam',img)
        cv2.waitKey(1)

        if keyboard.is_pressed('q'):
            print("i quit!!")
            cv2.destroyWindow('webcam')
            break



# mark attendance
def attendance():
    ff = open("Attendance.csv", 'w+')
    ss = ""
    try:
        ff.writelines("NAME,ENTRY,EXIT,TIME_SPENT_IN_MIN")
        ff.writelines("\n")
        del attend_dict['NAME']
        del attend_dict['UNKNOWN']
    except KeyError:
        print()

    for i in (attend_dict.keys()):
        ss += i
        entryy=attend_dict[i][0]
        exitt=attend_dict[i][1]
        try:
            ts=(int(exitt[3:-3]) - int(entryy[3:-3])) + (60*(int(exitt[:2]) - int(entryy[:2]) ))
            ss += "," + entryy + "," + exitt + "," + str(ts)
            ff.writelines(ss)
            ff.writelines("\n")
        except ValueError:
            print()

        ss = ""

    ff.close()
    os.startfile(r"Attendance.csv")


# take a new pic from webcam
def take_a_pic():
    new_name = pyautogui.prompt('What is your name?',title="Name",default="new_image")

    if new_name in del_names:
        loc=del_ind[del_names.index(new_name)]
        image_names[loc]=new_name

        new_name += ".jpg"
        tk.messagebox.showinfo("Alert", "Look at the Camera in 3 sec !")
        result, new_img = cv2.VideoCapture(0).read()
        cv2.imwrite(rf"ImagesAttendance\{new_name}", new_img)
        cv2.imshow("New Image", new_img)
        cv2.waitKey(0)
        cv2.destroyWindow('New Image')

    else:
        new_name+= ".jpg"
        tk.messagebox.showinfo("Alert", "Look at the Camera in 3 sec !")
        result, new_img = cv2.VideoCapture(0).read()
        cv2.imwrite(rf"ImagesAttendance\{new_name}",new_img)
        cv2.imshow("New Image",new_img)
        cv2.waitKey(0)
        cv2.destroyWindow('New Image')

        images.append(cv2.imread(fr'ImagesAttendance\{new_name}'))
        image_names.append(os.path.splitext(new_name)[0])
        print(os.path.splitext(new_name)[0])
        encodeList.append(face_recognition.face_encodings(images[-1])[0])


def open_images_to_delete():
    L1 = image_names
    L2 = []
    li2 = os.listdir(r"ImagesAttendance")
    filesz = filedialog.askopenfilenames(title = "Select image files", filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
    print("Selected files:", filesz)
    for xx in filesz:
        os.remove(xx)
        xx = os.path.splitext(xx[xx.find('nce') + 4:])[0]
        #set_dif.append(os.path.splitext(xx)[0])
        del_ind.append(L1.index(xx))
        del_names.append(image_names[L1.index(xx)])
        image_names[L1.index(xx)] = "unknown"
        print("removed : ", xx)

    set_dif = []
    for x in li2:
        L2.append(os.path.splitext(x)[0])
    set_dif = list(set(L1).symmetric_difference(set(L2)))
    set_dif = list(filter(lambda t: t != "unknown", set_dif))
    removed_names = ""
    for j in set_dif:
        removed_names += j + " , "
    tk.messagebox.showinfo("showinfo", f"Faces removed = {len(set_dif)}\n{removed_names}\nClose the Window")


def delete_a_face():
    root1 = tk.Toplevel()
    root1.geometry("310x220")
    root1.title("delete")
    image2 = PhotoImage(file='delete.png')
    bg1label = tk.Label(root1, image=image2, width=300, height=180)
    bg1label.pack()
    button9 = tk.Button(root1, text="Select the images", command=open_images_to_delete, width=300,pady=5)
    button9.pack()
    root1.mainloop()


def show():
    os.startfile(r"only_name")


def know_faces():
    os.startfile(r"ImagesAttendance")


def about():
    os.startfile(r"ABOUT OURSELVES.png")

#############----Mainn-------#############


clean() # empty the known images folder
access() # get the names of images
encodeListKnown = find_encodings(images) # encode all the images
print("Encoding Completed..")

# GUIIIII

imag = tk.PhotoImage(file="bg4.png")

frame = cstk.CTkFrame(master=root)
frame.pack(padx=60,pady=20,fill="both",expand=True)

label = cstk.CTkLabel(master=frame,text="Facial Recognition System",font=("Roboto",24),compound="left")
label.pack(pady=12,padx=10)

bglabel = cstk.CTkLabel(master=frame,image=imag,text="", width=1080,height=1080)
bglabel.pack()

button1 = cstk.CTkButton(master=frame,text="Scan face (Webcam)",command=webcam_scan,height=80,width=250,font=("Arial",24))
button1.place(relx=0.3,rely=0.3,anchor="e")

button4 = cstk.CTkButton(master=frame,text="Known Images",command=know_faces,height=80,width=250,font=("Arial",24))
button4.place(relx=0.75,rely=0.3,anchor="w")

button5 = cstk.CTkButton(master=frame,text="Add a new face",command=take_a_pic,height=80,width=250,font=("Arial",24))
button5.place(relx=0.3,rely=0.57,anchor="e")

button6 = cstk.CTkButton(master=frame,text="Delete a face",command=delete_a_face,height=80,width=250,font=("Arial",24))
button6.place(relx=0.75,rely=0.562,anchor="w")

button3 = cstk.CTkButton(master=frame,text="About",command=about,height=80,width=250,font=("Arial",24))
button3.place(relx=0.3,rely=0.85,anchor="e")

button2 = cstk.CTkButton(master=frame,text="Show Scanned Images",command=show,height=80,width=250,font=("Arial",24))
button2.place(relx=0.75,rely=0.85,anchor="w")

button7 = cstk.CTkButton(master=frame,text="Open Attendance",command=attendance,height=80,width=250,font=("Arial",24))
button7.place(relx=0.52,rely=0.5,anchor="center")

root.mainloop()

