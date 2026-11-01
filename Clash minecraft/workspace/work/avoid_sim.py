import math
def segbox(ax,az,bx,bz,b):
    t0,t1=0.0,1.0; dx,dz=bx-ax,bz-az
    p=[-dx,dx,-dz,dz]; q=[ax-b[0],b[2]-ax,az-b[1],b[3]-az]
    for i in range(4):
        if abs(p[i])<1e-9:
            if q[i]<0: return -1
        else:
            r=q[i]/p[i]
            if p[i]<0:
                if r>t1: return -1
                if r>t0: t0=r
            else:
                if r<t0: return -1
                if r<t1: t1=r
    return t0 if t0<=t1 else -1
def merge(boxes,r):
    bs=[list(b) for b in boxes]
    ch=True
    while ch:
        ch=False
        for i in range(len(bs)):
            for j in range(i+1,len(bs)):
                a,b=bs[i],bs[j]
                g=2*r+0.1
                if a[0]-g<b[2] and b[0]-g<a[2] and a[1]-g<b[3] and b[1]-g<a[3]:
                    bs[i]=[min(a[0],b[0]),min(a[1],b[1]),max(a[2],b[2]),max(a[3],b[3])]; del bs[j]; ch=True; break
            if ch: break
    return bs
def avoid(fx,fz,wx,wz,boxes,r):
    hit=None;best=2
    for b in merge(boxes,r):
        if b[0]-r<wx<b[2]+r and b[1]-r<wz<b[3]+r: continue
        e=[b[0]-r+.05,b[1]-r+.05,b[2]+r-.05,b[3]+r-.05]
        t=segbox(fx,fz,wx,wz,e)
        if 0<=t<best: best=t;hit=b;hitE=e
    if hit is None: return wx,wz
    m=r+.45
    cs=[(hit[0]-m,hit[1]-m),(hit[2]+m,hit[1]-m),(hit[2]+m,hit[3]+m),(hit[0]-m,hit[3]+m)]
    bi=-1;bc=1e18
    for p in range(2):
        if bi>=0: break
        for i,(cx,cz) in enumerate(cs):
            if p==0 and segbox(fx,fz,cx,cz,hitE)>=0: continue
            d0=math.hypot(cx-fx,cz-fz)
            if segbox(cx,cz,wx,wz,hitE)<0: rest=math.hypot(wx-cx,wz-cz)
            else:
                rest=min(math.hypot(cs[(i+k)%4][0]-cx,cs[(i+k)%4][1]-cz)+math.hypot(wx-cs[(i+k)%4][0],wz-cs[(i+k)%4][1]) for k in (-1,1))
            if d0+rest<bc: bc=d0+rest;bi=i
    return cs[bi] if bi>=0 else (wx,wz)
def push(x,z,boxes,r):
    for b in boxes:
        if x<b[0]-r or x>b[2]+r or z<b[1]-r or z>b[3]+r: continue
        qx=max(b[0],min(b[2],x)); qz=max(b[1],min(b[3],z))
        if qx==x and qz==z:
            l,rr,t,bt=x-b[0],b[2]-x,z-b[1],b[3]-z; m=min(l,rr,t,bt)
            if m==l: x=b[0]-r
            elif m==rr: x=b[2]+r
            elif m==t: z=b[1]-r
            else: z=b[3]+r
        else:
            dx,dz=x-qx,z-qz; d=math.hypot(dx,dz)
            if d<r: x=qx+dx/d*r; z=qz+dz/d*r
    return x,z
def run(start,goal,boxes,r=0.5,use=True,steps=1500):
    x,z=start
    for i in range(steps):
        wx,wz=avoid(x,z,goal[0],goal[1],boxes,r) if use else goal
        dx,dz=wx-x,wz-z; d=math.hypot(dx,dz)
        if math.hypot(goal[0]-x,goal[1]-z)<0.3: return i
        if d>1e-9:
            s=min(d,0.1); x+=dx/d*s; z+=dz/d*s
        x,z=push(x,z,boxes,r)
    return None
tower=[0,0,9,9]
cases=[((4.5,-3),(4.5,20)),((4.4,-0.6),(4.5,20)),((-0.6,4.5),(15,4.5)),((4.5,-3),(4.6,12)),((9.6,-0.6),(-3,12)),((4.5,-3),(4.5,9.6))]
for st,g in cases:
    print(st,g,'old',run(st,g,[tower],use=False),'new',run(st,g,[tower]))
# two boxes (tower + building next to it)
b2=[[0,0,9,9],[9.5,3,13.5,7]]
print('2box',run((6,-3),(8,20),b2,r=0.6))
print('big r',run((4.5,-3),(4.5,20),[tower],r=1.1))
