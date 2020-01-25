from tkinter import *
from tkinter import ttk, filedialog
from PIL import ImageTk, Image

class Root(Tk):
    def __init__(self):
        super(Root, self).__init__()
        self.title("Dialog Screen")
        self.minsize(640, 400)
        #self.wm_iconbitmap('icon.ico')

        self.info = "Information will appear here"

        self.labelFrame = ttk.LabelFrame(self, text = "Open Example Image")
        self.labelFrame.grid(column = 2, row = 1, padx = 20, pady = 20)
        self.infoFrame = Label(self, text = self.info)
        self.infoFrame.grid(column = 2, row = 2, padx = 20, pady = 20)    # Solve this?

        self.draw = False
        self.hold = False
        self.startCoords = None
        self.digits = []
        self.coords = []
        
        self.browseButton()

    def browseButton(self):
        self.button = Button(self.labelFrame, text = "Browse An Image", command = self.fileDialog)
        self.button.grid(column = 2, row = 1)

    def drawButtons(self):
        self.draw_button = Button(self, text = "Add a digit", command = (lambda self=self: exec("self.draw = not self.draw")))
        self.draw_button.grid(column = 2, row = 3)

        self.undo_button = Button(self, text = "Undo Action", command = self.undoAction)
        self.undo_button.grid(column = 2, row = 5)

        self.fin_button = Button(self, text = "Finish", command = self.finish)
        self.fin_button.grid(column = 2, row = 6)

    def undoAction(self):
        try: 
            self.panel.delete(self.digits[-1])
            del self.digits[-1]
            del self.coords[-1]
            self.infoFrame.configure(text = self.info.format(self.dimensions[::-1], len(self.digits)))
        except:
            pass        

    def fileDialog(self):
        self.filename = filedialog.askopenfilename(initialdir = "C:\\Users\\puria\\source\\repos\\puria-radmard\\CambridgeCarbonMap\\MLsec", title = "Select A File", filetype = (("jpeg files", "*.jpg"), ("png files", "*.png")))
        self.label = ttk.Label(self.labelFrame, text = "")
        self.label.grid(column = 2, row = 2)
        self.label.configure(text = self.filename)
        self.displayImage()

    def displayImage(self):
        self.plan = ImageTk.PhotoImage(Image.open(self.filename))
        self.dimensions = [self.plan.height(), self.plan.width()]
        #self.panel = Label(self, image = self.plan)
        #self.panel.grid(column = 2, row = 4)

        self.panel = Canvas(self, width = self.dimensions[1], height = self.dimensions[0])
        self.panel.grid(column = 2, row = 4)
        self.panel.create_image([i/2 for i in self.dimensions[::-1]], image = self.plan)

        self.panel.bind("<Motion>", func = self.panelOver)
        self.panel.bind("<Button-1>", func = self.panelDraw)
        self.panel.bind("<Leave>", func = self.exitFrame)
        self.panel.bind("<ButtonRelease-1>", func = self.dropDigit)

        self.info = "Dimensions: {}     Digits Added: {}"
        self.infoFrame.configure(text = self.info.format(self.dimensions[::-1], 0))

        self.tempRect = self.panel.create_rectangle(80, 80, 50, 50, outline = "blue", width = 5)
        self.panel.delete(self.tempRect)

        self.drawButtons()

    def exitFrame(self, e):
        try:
            self.panel.delete(self.tempRect)
        except:
            pass

    def panelOver(self, e):

        try:
            self.panel.delete(self.tempRect)
        except:
            pass

        if self.draw and self.hold:
            
            self.tempRect = self.panel.create_rectangle(self.startCoords[0], self.startCoords[1], e.x, e.y, outline = "blue", width = 5)
            
        else:
            pass

    def panelDraw(self, e):

        if self.draw:
            print(e.x, e.y, "Clicked")

            self.hold = True
            if self.startCoords == None: 
                self.startCoords = (e.x, e.y)


        else:
            pass

    def dropDigit(self, e):
        if self.draw:
            a =  self.panel.create_rectangle(self.startCoords[0], self.startCoords[1], e.x, e.y, outline = "blue", width = 5)
            self.digits.append(a)
            self.infoFrame.configure(text = self.info.format(self.dimensions[::-1], len(self.digits)))
            
            self.coords.append((self.startCoords, (e.x, e.y)))
            self.startCoords = None
            print("wow")
            #print(self.coords)
            #self.
            self.hold = False
        else:
            pass

    def finish(self):
        print(self.coords)
        self.coords.sort()
        self.destroy()


root = Root()
root.mainloop()

#string1 = "dimension: {}"
#string2 = string1.format("500x500, leftest: {}")
#print(string2.format(95))