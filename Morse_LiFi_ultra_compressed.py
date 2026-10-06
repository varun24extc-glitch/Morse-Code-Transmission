import tkinter as tk
from tkinter import messagebox
import random

M=dict(zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
[".-","-...","-.-.","-..",".","..-.","--.","....","..",".---","-.-",".-..","--","-.","---",".--.","--.-",".-.","...","-","..-","...-",".--","-..-","-.--","--..","-----",".----","..---","...--","....-",".....","-....","--...","---..","----."]))
R={v:k for k,v in M.items()}

def enc(s):return " / ".join(" ".join(M[c] for c in w if c in M) for w in s.upper().split())
def dec(s):return " ".join("".join(R.get(c,"") for c in w.split()) for w in s.split(" / "))
def sig(s):
    a=[]
    for wi,w in enumerate(s.split(" / ")):
        for li,l in enumerate(w.split()):
            for si,c in enumerate(l):a += [1]*(1 if c=="." else 3)+([0] if si<len(l)-1 else [])
            if li<len(w.split())-1:a += [0]*3
        if wi<len(s.split(" / "))-1:a += [0]*7
    return a
def unsig(a):
    if not a:return ""
    z=[];c=a[0];n=1
    for x in a[1:]:
        if x==c:n+=1
        else:z.append((c,n));c=x;n=1
    z.append((c,n));w=[];l=""
    for x,n in z:
        if x:l += "." if n<=1 else "-"
        elif n>=7:
            if l:w.append(l)
            if w and (not w[-1].endswith(" / ")):w[-1]+=" / "
            l=""
        elif n>=3:
            if l:w.append(l);l=""
    if l:w.append(l)
    return " ".join(w).replace(" /  "," / ")

class App:
    def __init__(self,r):
        self.r=r;r.title("Morse Code Transmission Using LiFi");r.geometry("1200x850");r.configure(bg="#101820")
        self.s=self.rs=[];self.p=self.err=self.bits=0;self.run=0
        L=lambda x,t,f=("Arial",12),bg="#101820":tk.Label(x,text=t,font=f,bg=bg,fg="white")
        L(r,"MORSE CODE TRANSMISSION USING LiFi",("Arial",24,"bold")).pack(pady=10)
        L(r,"Software-Based Digital Communication Simulation",("Arial",11)).pack()
        f=tk.Frame(r,bg="#18242d");f.pack(fill="x",padx=20,pady=12)
        L(f,"MESSAGE:",("Arial",12,"bold"),"#18242d").pack(side="left",padx=8)
        self.e=tk.Entry(f,font=("Arial",14),width=30);self.e.pack(side="left",padx=8);self.e.insert(0,"SOS")
        tk.Button(f,text="TRANSMIT",command=self.start).pack(side="left",padx=5)
        tk.Button(f,text="RESET",command=self.reset).pack(side="left")
        self.ml=L(r,"Morse Code: ---",("Courier New",16,"bold"));self.ml.pack(pady=4)
        c=tk.Frame(r,bg="#18242d");c.pack(fill="x",padx=20,pady=5)
        L(c,"Distance:",bg="#18242d").grid(row=0,column=0,padx=5)
        self.d=tk.DoubleVar(value=2);tk.Scale(c,from_=1,to=10,resolution=.5,orient="horizontal",variable=self.d,command=self.control,bg="#18242d",fg="white",highlightthickness=0,length=180).grid(row=0,column=1)
        self.dv=L(c,"2.0 m",bg="#18242d");self.dv.grid(row=0,column=2,padx=8)
        L(c,"Noise:",bg="#18242d").grid(row=0,column=3)
        self.n=tk.DoubleVar();tk.Scale(c,from_=0,to=30,orient="horizontal",variable=self.n,command=self.control,bg="#18242d",fg="white",highlightthickness=0,length=180).grid(row=0,column=4)
        self.nv=L(c,"0%",bg="#18242d");self.nv.grid(row=0,column=5)
        s=tk.Frame(r,bg="#101820");s.pack(pady=8)
        self.tx=self.device(s,"TRANSMITTER",0);L(s,"💡 ───────── LiFi LIGHT ─────────> 📡",("Arial",15,"bold")).grid(row=0,column=1,padx=15)
        self.rx=self.device(s,"RECEIVER",2)
        L(r,"DIGITAL SIGNAL WAVEFORMS",("Arial",15,"bold")).pack(pady=5)
        self.w=tk.Canvas(r,width=1100,height=200,bg="black");self.w.pack()
        q=tk.Frame(r,bg="#18242d");q.pack(fill="x",padx=20,pady=8)
        self.rm=L(q,"Received Morse: ---",("Courier New",12,"bold"),"#18242d");self.rm.grid(row=0,column=0,padx=20,pady=5)
        self.out=L(q,"Received Message: ---",("Arial",14,"bold"),"#18242d");self.out.grid(row=0,column=1,padx=20)
        self.bi=L(q,"Bits: 0 | Errors: 0 | BER: 0.0000",bg="#18242d");self.bi.grid(row=1,column=0,columnspan=2)
        self.st=L(r,"SYSTEM READY",("Arial",12,"bold"));self.st.pack()

    def device(self,p,t,col):
        f=tk.Frame(p,bg="#18242d",width=200,height=170);f.grid(row=0,column=col,padx=10);f.pack_propagate(False)
        tk.Label(f,text=t,font=("Arial",16,"bold"),bg="#18242d",fg="white").pack(pady=5)
        x=tk.Canvas(f,width=100,height=90,bg="#202a32");x.pack();z=x.create_oval(20,15,80,75,fill="gray")
        l=tk.Label(f,text="OFF",bg="#18242d",fg="white");l.pack()
        return x,z,l

    def control(self,*_):
        self.dv.config(text=f"{self.d.get():.1f} m");self.nv.config(text=f"{self.n.get():.0f}%")

    def start(self):
        if self.run:return
        m=enc(self.e.get().strip())
        if not m:return messagebox.showwarning("Input Error","Enter letters or numbers.")
        self.ml.config(text="Morse Code: "+m);self.s=sig(m);self.bits=len(self.s);self.err=0;self.rs=[]
        p=min(.95,max(0,(self.d.get()-2)*.015)+self.n.get()/100)
        for b in self.s:
            x=1-b if random.random()<p else b;self.err+=x!=b;self.rs.append(x)
        self.p=0;self.run=1;self.st.config(text="TRANSMITTING LiFi SIGNAL...");self.animate()

    def led(self,a,on):
        a[0].itemconfig(a[1],fill="white" if on else "gray");a[2].config(text="ON" if on else "OFF")

    def animate(self):
        if self.p>=self.bits:return self.finish()
        self.led(self.tx,bool(self.s[self.p]));self.led(self.rx,bool(self.rs[self.p]));self.wave();self.p+=1;self.r.after(100,self.animate)

    def wave(self):
        self.w.delete("all")
        for j,a in enumerate((self.s,self.rs)):
            pts=[];start=max(0,self.p-70)
            for i in range(start,self.p+1):pts.append((100+(i-start)*1000/70,35+j*90 if a[i] else 65+j*90))
            for x,y in zip(pts,pts[1:]):self.w.create_line(*x,*y,fill=("lime","cyan")[j],width=2)

    def finish(self):
        self.run=0;self.led(self.tx,0);self.led(self.rx,0);m=unsig(self.rs);self.rm.config(text="Received Morse: "+m);self.out.config(text="Received Message: "+dec(m));self.bi.config(text=f"Bits: {self.bits} | Errors: {self.err} | BER: {self.err/self.bits:.4f}");self.st.config(text="TRANSMISSION COMPLETED")

    def reset(self):
        self.run=0;self.s=self.rs=[];self.p=self.err=self.bits=0;self.led(self.tx,0);self.led(self.rx,0);self.ml.config(text="Morse Code: ---");self.rm.config(text="Received Morse: ---");self.out.config(text="Received Message: ---");self.bi.config(text="Bits: 0 | Errors: 0 | BER: 0.0000");self.w.delete("all");self.st.config(text="SYSTEM READY")

root=tk.Tk();App(root);root.mainloop()
