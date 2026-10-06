import tkinter as tk
from tkinter import messagebox
import random

M=dict(zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
[".-","-...","-.-.","-..",".","..-.","--.","....","..",".---","-.-",".-..","--","-.","---",".--.","--.-",".-.","...","-","..-","...-",".--","-..-","-.--","--..","-----",".----","..---","...--","....-",".....","-....","--...","---..","----."]))
R={v:k for k,v in M.items()}

def enc(s): return " / ".join(" ".join(M[c] for c in w if c in M) for w in s.upper().split())
def dec(s): return " ".join("".join(R.get(c,"") for c in w.split()) for w in s.split(" / "))
def sig(s):
    a=[]
    for wi,w in enumerate(s.split(" / ")):
        for li,l in enumerate(w.split()):
            for si,c in enumerate(l):
                a += [1]*(1 if c=="." else 3)
                if si<len(l)-1:a+=[0]
            if li<len(w.split())-1:a += [0]*3
        if wi<len(s.split(" / "))-1:a += [0]*7
    return a

def unsig(a):
    if not a:return ""
    r=[];v=a[0];n=1
    for x in a[1:]:
        if x==v:n+=1
        else:r.append((v,n));v=x;n=1
    r.append((v,n)); words=[];letters=[];cur=""
    for v,n in r:
        if v:
            cur += "." if n<=1 else "-"
        elif n>=7:
            if cur:letters.append(cur);cur=""
            if letters:words.append(" ".join(letters));letters=[]
        elif n>=3:
            if cur:letters.append(cur);cur=""
    if cur:letters.append(cur)
    if letters:words.append(" ".join(letters))
    return " / ".join(words)

class App:
    def __init__(self,r):
        self.r=r;r.title("Morse Code Transmission Using LiFi");r.geometry("1280x950");r.configure(bg="#101820")
        self.s=self.rs=[];self.p=self.err=self.bits=0;self.run=0;self.speed=120
        self.d=tk.DoubleVar(value=2);self.n=tk.DoubleVar(value=0)
        self.title(r,"MORSE CODE TRANSMISSION USING LiFi",25);self.title(r,"Software-Based Digital Communication Simulation",12)
        f=tk.Frame(r,bg="#18242d");f.pack(fill="x",padx=25,pady=12)
        self.lab(f,"MESSAGE:",13,"#18242d").pack(side="left",padx=10)
        self.e=tk.Entry(f,font=("Arial",15),width=30);self.e.pack(side="left",padx=10);self.e.insert(0,"SOS")
        for t,c in [("TRANSMIT",self.start),("STOP",self.stop),("RESET",self.reset)]:tk.Button(f,text=t,command=c,font=("Arial",11,"bold"),padx=12).pack(side="left",padx=4)
        self.ml=self.lab(r,"Morse Code: ---",18);self.ml.pack(pady=5)

        c=tk.Frame(r,bg="#18242d");c.pack(fill="x",padx=25,pady=8)
        self.lab(c,"Distance:",12,"#18242d").grid(row=0,column=0)
        tk.Scale(c,from_=1,to=10,resolution=.5,orient="horizontal",variable=self.d,command=self.ctrl,length=220,bg="#18242d",fg="white",highlightthickness=0).grid(row=0,column=1)
        self.dv=self.lab(c,"2.0 m",12,"#18242d");self.dv.grid(row=0,column=2,padx=5)
        self.lab(c,"Noise:",12,"#18242d").grid(row=0,column=3)
        tk.Scale(c,from_=0,to=30,orient="horizontal",variable=self.n,command=self.ctrl,length=220,bg="#18242d",fg="white",highlightthickness=0).grid(row=0,column=4)
        self.nv=self.lab(c,"0%",12,"#18242d");self.nv.grid(row=0,column=5,padx=5)
        self.info=self.lab(c,"Strength: 100% | SNR: 30 dB | Channel: GOOD",11,"#18242d");self.info.grid(row=1,column=0,columnspan=6,pady=5)

        z=tk.Frame(r,bg="#101820");z.pack(pady=8)
        self.tx=self.device(z,"TRANSMITTER",0);self.lab(z,"💡 ───────── LiFi OPTICAL CHANNEL ─────────> 📡",16).grid(row=0,column=1,padx=12)
        self.rx=self.device(z,"RECEIVER",2)

        self.lab(r,"TRANSMITTED vs RECEIVED DIGITAL SIGNAL",15).pack(pady=5)
        self.w=tk.Canvas(r,width=1150,height=220,bg="black");self.w.pack(padx=25)
        q=tk.Frame(r,bg="#18242d");q.pack(fill="x",padx=25,pady=8)
        self.rm=self.lab(q,"Received Morse: ---",13,"#18242d");self.rm.grid(row=0,column=0,padx=20)
        self.out=self.lab(q,"Received Message: ---",14,"#18242d");self.out.grid(row=0,column=1,padx=20)
        self.st=self.lab(r,"Bits: 0 | Errors: 0 | BER: 0.0000",11);self.st.pack()
        b=tk.Frame(r,bg="#101820");b.pack(pady=8)
        for t,c in [("BER vs NOISE",self.noise_exp),("BER vs DISTANCE",self.dist_exp),("CLEAR GRAPHS",self.clear)]:tk.Button(b,text=t,command=c,padx=10).pack(side="left",padx=5)
        self.status=self.lab(r,"SYSTEM READY",12);self.status.pack(pady=4)

    def title(self,r,t,n):
        self.lab(r,t,n).pack(pady=8 if n>20 else 0)
    def lab(self,p,t,n,bg="#101820"):
        return tk.Label(p,text=t,font=("Arial",n,"bold" if n>=15 else "normal"),fg="white",bg=bg)
    def device(self,p,t,col):
        f=tk.Frame(p,bg="#18242d",width=260,height=200);f.grid(row=0,column=col,padx=12);f.pack_propagate(False)
        self.lab(f,t,17,"#18242d").pack(pady=8);x=tk.Canvas(f,width=120,height=120,bg="#202a32");x.pack()
        o=x.create_oval(28,28,92,92,fill="gray");l=self.lab(f,"OFF",10,"#18242d");l.pack();return x,o,l
    def led(self,a,on,rx=False):
        a[0].itemconfig(a[1],fill="cyan" if rx and on else "white" if on else "gray");a[2].config(text="LIGHT DETECTED" if rx and on else "LED ON → LIGHT 1" if on else "NO LIGHT" if rx else "LED OFF → LIGHT 0")
    def ctrl(self,*_):
        d=self.d.get();n=self.n.get();self.dv.config(text=f"{d:.1f} m");self.nv.config(text=f"{n:.0f}%")
        strength=max(5,min(100,100/(1+.12*(d-1)**2)));snr=max(-10,30-n*.75-(d-1)*1.2)
        ch="GOOD" if snr>=20 else "MODERATE" if snr>=10 else "POOR";self.info.config(text=f"Strength: {strength:.1f}% | SNR: {snr:.1f} dB | Channel: {ch}")
    def prob(self,d,n):return min(.90,max(0,(d-2)*.018)+n/100)
    def start(self):
        if self.run:return
        m=self.e.get().strip().upper()
        if not m:return messagebox.showwarning("Input Error","Please enter a message.")
        mo=enc(m)
        if not mo:return messagebox.showwarning("Input Error","Enter valid letters or numbers.")
        self.s=sig(mo);self.bits=len(self.s);self.err=0;self.rs=[];p=self.prob(self.d.get(),self.n.get())
        for b in self.s:
            x=1-b if random.random()<p else b;self.err+=x!=b;self.rs.append(x)
        self.ml.config(text="Morse Code: "+mo);self.p=0;self.run=1;self.status.config(text="TRANSMITTING LiFi SIGNAL...");self.animate()
    def animate(self):
        if not self.run:return
        if self.p>=self.bits:return self.finish()
        self.led(self.tx,self.s[self.p]);self.led(self.rx,self.rs[self.p],1);self.wave();self.p+=1;self.r.after(self.speed,self.animate)
    def wave(self):
        self.w.delete("all");st=max(0,self.p-65);en=self.p;step=1050/max(1,en-st)
        self.w.create_text(10,30,text="TRANSMITTED",fill="white",anchor="w");self.w.create_text(10,135,text="RECEIVED",fill="white",anchor="w")
        for a,y,col in [(self.s,45,"lime"),(self.rs,150,"cyan")]:
            for i in range(st+1,en):
                x1=100+(i-1-st)*step;x2=100+(i-st)*step;y1=y if a[i-1] else y+25;y2=y if a[i] else y+25
                self.w.create_line(x1,y1,x2,y1,fill=col,width=3);self.w.create_line(x2,y1,x2,y2,fill=col,width=3)
    def finish(self):
        self.run=0;self.led(self.tx,0);self.led(self.rx,0,1);mo=unsig(self.rs);self.rm.config(text="Received Morse: "+(mo or "---"));self.out.config(text="Received Message: "+(dec(mo) or "---"));self.st.config(text=f"Bits: {self.bits} | Errors: {self.err} | BER: {self.err/self.bits:.4f}");self.status.config(text="TRANSMISSION COMPLETED")
    def stop(self):
        self.run=0;self.led(self.tx,0);self.led(self.rx,0,1);self.status.config(text="TRANSMISSION STOPPED")
    def reset(self):
        self.run=0;self.s=self.rs=[];self.p=self.err=self.bits=0;self.led(self.tx,0);self.led(self.rx,0,1);self.ml.config(text="Morse Code: ---");self.rm.config(text="Received Morse: ---");self.out.config(text="Received Message: ---");self.st.config(text="Bits: 0 | Errors: 0 | BER: 0.0000");self.w.delete("all");self.status.config(text="SYSTEM READY")
    def experiment(self,typ):
        m=enc(self.e.get().strip().upper() or "SOS");a=sig(m)
        xs=range(0,31,5) if typ=="noise" else range(1,11);data=[]
        for x in xs:
            e=0
            for _ in range(20):
                p=self.prob(2,x) if typ=="noise" else self.prob(x,0)
                e+=sum(random.random()<p for _ in a)
            data.append((x,e/(len(a)*20)))
        self.graph("BER vs "+("CHANNEL NOISE" if typ=="noise" else "LiFi DISTANCE"),"Noise (%)" if typ=="noise" else "Distance (m)",data)
    def noise_exp(self):self.experiment("noise")
    def dist_exp(self):self.experiment("distance")
    def graph(self,title,xlab,data):
        g=tk.Toplevel(self.r);g.title(title);g.geometry("850x600");g.configure(bg="#101820");self.lab(g,title,18).pack(pady=10)
        c=tk.Canvas(g,width=780,height=480,bg="black");c.pack();L,R,T,B=80,730,40,410;mx=max(y for x,y in data) or 1;xx=max(x for x,y in data) or 1
        c.create_line(L,B,R,B,fill="white",width=2);c.create_line(L,B,L,T,fill="white",width=2)
        for i in range(6):
            y=B-i*(B-T)/5;c.create_line(L,y,R,y,fill="#333");c.create_text(L-10,y,text=f"{mx*i/5:.3f}",fill="white",anchor="e")
        prev=None
        for x,y in data:
            px=L+x/xx*(R-L);py=B-y/mx*(B-T);c.create_oval(px-4,py-4,px+4,py+4,fill="white")
            if prev:c.create_line(*prev,px,py,fill="white",width=2)
            prev=(px,py);c.create_text(px,B+15,text=str(x),fill="white")
        c.create_text(400,470,text=xlab,fill="white",font=("Arial",12,"bold"));c.create_text(20,220,text="BER",fill="white",angle=90,font=("Arial",12,"bold"))
    def clear(self):self.status.config(text="EXPERIMENT DATA CLEARED")

root=tk.Tk();App(root);root.mainloop()
