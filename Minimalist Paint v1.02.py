import tkinter as tk
from PIL import Image, ImageDraw
from functools import partial

version = " v"+str(float(1.02))
icon = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAnElEQVR4nO2XwQnAIAxFc3AH13ELZ3QL13GKFgI5VJCYUGjkN5ccauTx8xNsIqKLHFFK4Zxz5txa81xDyVX1YvwAZoC592MMzrVWzlYvnKcALoA29/Ld6oVzFMAF2N35vffH+V0vxFcAF2DuvTc0L8RVABdgNffafHvr4imAC6Dt/NWulzehtU7OxVEAF8D6jzf31FsnXvheAXiAG3LNSsr+aWabAAAAAElFTkSuQmCC'

class MinimalisticPaint(tk.Canvas):
    def __init__(self, parent, *args, **kwargs):
        tk.Canvas.__init__(self, parent, *args, **kwargs)

        ## VARIABLES (COLORS) ##
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)
        self.blue = (0, 0, 255)
        self.red = (255, 0, 0)
        self.green = (0,128,0)
        
        ## VARIABLES (PROGRAM) ##
        self.parent = parent
        self._width = self.parent.winfo_screenwidth()
        self._height = self.parent.winfo_screenheight()
        self.image = Image.new("RGB", (self._width, self._height), self.white)
        self.draw_image = ImageDraw.Draw(self.image)
        self.filename = "test_name"
        self.extension = ".png"
        self.in_shape = "line"
        self.in_color = "#000000" # clear is None
        self.in_mode = "draw" # "erase"
        self.in_size = 10
        self.framerate = 1 #int(1000.0/60.0)
        self.main_input = [(0,0),'']
        self.line_lastpos = [0,0]
##        print(self.line_lastpos)
##        print(type(self.line_lastpos))

        ## WINDOW ##
        self._geom = "{}x{}+0+0".format(self._width,self._height)
        self.parent.geometry(self._geom)

        ## MENU ##
        self.menubar = tk.Menu(self.parent)
        
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Open", command=self.ignore)
        self.filemenu.add_command(label="Save", command=self.save)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.parent.destroy)
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        
        self.editmenu = tk.Menu(self.menubar, tearoff=0)
        self.editmenu.add_command(label="Cut", command=self.ignore)
        self.editmenu.add_command(label="Copy", command=self.ignore)
        self.editmenu.add_command(label="Paste", command=self.ignore)
        self.menubar.add_cascade(label="Edit", menu=self.editmenu)

        self.helpmenu = tk.Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(label="About", command=self.ignore)
        self.helpmenu.add_command(label="Guide", command=self.open_guide)
        self.menubar.add_cascade(label="Help", menu=self.helpmenu)
        
        self.menubar.add_cascade(label="Fullscreen", command=partial(self.parent.geometry, '+0+0'))
        
        self.parent.config(menu=self.menubar)

        ## TOOLBAR ##

        self.toolbar = tk.Toplevel()
        self.tb_list = [tk.Radiobutton(self.toolbar, text='Draw', value=1, width=8, command=partial(self.toggle_mode, 'draw')),
                        tk.Radiobutton(self.toolbar, text='Erase', value=2, width=8, command=partial(self.toggle_mode, 'erase')),
                        tk.Radiobutton(self.toolbar, text='Fill', value=3, width=8, command=partial(self.toggle_mode, 'fill')),
                        tk.Button(self.toolbar, text='Undo', width=8, command=self.ignore, state='disabled'),
                        tk.Button(self.toolbar, text='Clear', width=8, command=self.main_clear)]
        for i in range(len(self.tb_list)):
            self.tb_list[i].pack(side='left')
            if i == 0: self.tb_list[i].select()
            if i in (1,2): self.tb_list[i].deselect()
        self.toolbar.title('Minimal\'s Toolbar')
        self.toolbar.protocol('WM_DELETE_WINDOW', self.ignore)
        self.toolbar.transient(self.parent)
        self.toolbar.resizable(0,0)
        self.toolbar.geometry('+{}+0'.format(int(self.toolbar.winfo_rootx()/2-self.toolbar.winfo_x()/2)))
        

        
        ## CANVAS INTERACTION ##
        self.canvas = tk.Canvas(self.parent, width=self._width, height=self._height)
        self.canvas.configure(background='white')
        # 1: Left, 2: Middle, 3: Right
        self.canvas.bind("<Button-1>", self.Button_1)
        self.canvas.bind("<Button-2>", self.pull_toolbar)
        self.canvas.bind("<Button-3>", self.Button_3)
        self.canvas.bind("<B1-Motion>", self.B1_Motion)
        self.canvas.bind("<B3-Motion>", self.B3_Motion)
        self.canvas.bind("<ButtonRelease-1>", self.ButtonRelease_1)
        self.canvas.bind("<ButtonRelease-3>", self.ButtonRelease_3)
        self.canvas.pack()
        
        self.guide = None
        self.guide_message = None
        self.guide_close = None

        self.parent.after(100, self.main_update)
        
        
        
    def pull_toolbar(self, event):
        self.toolbar.geometry('+{}+{}'.format(event.x_root, event.y_root))
        self.toolbar.lift()

##    def parent_fullscreen(self):
##        self.parent.geometry('+0+0')

    def ignore(self, *args, **kwargs):
        pass

    def open_guide(self):
        self.guide = tk.Toplevel()
        self.guide.title('Minimalist Guide')
        self.guide_message = tk.Message(self.guide, text='Middle Click to pull out toolbar')
        self.guide_message.pack()
        self.guide_close = tk.Button(self.guide, text='Close', command=self.close_guide)
        self.guide_close.pack()
    def close_guide(self):
        self.guide.destroy()
        self.guide = None
        self.guide_message = None
        self.guide_close = None


    def Button_1(self, pos):
        self.main_input = [(pos.x, pos.y), self.in_shape]
        self.line_lastpos = [pos.x, pos.y]
    def Button_3(self, pos):
        #if self.main_input[1] != '':
            
        return
        
    def B1_Motion(self, pos):
        self.main_input = [(pos.x, pos.y), self.in_shape]
    def B3_Motion(self, pos):
        return
    
    def ButtonRelease_1(self, pos):
        self.main_input = [(pos.x, pos.y), '']
    def ButtonRelease_3(self, pos):
        return
    
    def draw(self, pos, shape, size=0):
        size = self.in_size/2
        if shape == "line":
            self.canvas.create_line([pos[0], pos[1], self.line_lastpos[0], self.line_lastpos[1]], fill=("#ffffff" if self.in_mode == "erase" else self.in_color))#, outline="white" if self.in_mode == "erase" else self.in_color)
            self.draw_image.line([pos[0], pos[1], self.line_lastpos[0], self.line_lastpos[1]], fill=("#ffffff" if self.in_mode == "erase" else self.in_color))#, outline="white" if self.in_mode == "erase" else self.in_color)
        if shape == "rectangle":
            self.canvas.create_rectangle([pos.x-size, pos.y-size, pos.x+size, pos.y+size], fill="#ffffff" if self.in_mode == "erase" else self.in_color, outline="white" if self.in_mode == "erase" else self.in_color)
            self.draw_image.rectangle([pos.x-size, pos.y-size, pos.x+size, pos.y+size], fill="#ffffff" if self.in_mode == "erase" else self.in_color, outline="white" if self.in_mode == "erase" else self.in_color)
        if shape == "ellipse":
            self.canvas.create_oval([pos.x-size, pos.y-size, pos.x+size, pos.y+size], fill="#ffffff" if self.in_mode == "erase" else self.in_color, outline="white" if self.in_mode == "erase" else self.in_color)
            self.draw_image.ellipse([pos.x-size, pos.y-size, pos.x+size, pos.y+size], fill="#ffffff" if self.in_mode == "erase" else self.in_color, outline="white" if self.in_mode == "erase" else self.in_color)
        #if in_shape == "rectangle":
        
    def toggle_mode(self,mode):
        self.in_mode = mode

    def main_clear(self):
        self.canvas.delete("all")
        self.draw_image.rectangle([0,0,self._width,self._height], fill='#ffffff', outline='white')
        
    def save(self):
        self.canvas.update()
        self.parent.filename = tk.filedialog.asksaveasfile(mode = 'wb',
                                           defaultextension = ".png",
                                           filetypes = [("Portable Network Graphics (.png)","*.png"),
                                                        ("All files","*.*")])
        self.image.save(self.parent.filename)

        

    #def pending(self):
        
    def main_update(self):
        #self.line_lastpos = self.main_input[0]
        self.draw(self.main_input[0],self.main_input[1])
        self.parent.after(self.framerate, self.main_update)
        self.parent.after(self.framerate, self.second_update)
    def second_update(self):
        self.line_lastpos = self.main_input[0]

if __name__ == "__main__":
    root = tk.Tk()
    MinimalisticPaint(root).pack(side="top", fill="both", expand=True)
    root.title("Minimalist Paint"+version)
    root.state('zoomed') # maximize window (shows menu and taskbar)
    icon = tk.PhotoImage(data=icon)
    root.wm_iconphoto(True, icon)
    root.resizable(False, False)
    #root.protocol("WM_DELETE_WINDOW", lambda x:x)
    root.mainloop()










