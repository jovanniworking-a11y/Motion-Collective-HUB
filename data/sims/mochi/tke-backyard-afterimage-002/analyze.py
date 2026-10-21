import json,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
z=20;ox,oy=239574,431652;lat0=30.285242
mpp=156543.03392*math.cos(math.radians(lat0))/2**z
def px(lon,lat):
    n=2**z;x=(lon+180)/360*n;r=math.radians(lat);y=(1-math.asinh(math.tan(r))/math.pi)/2*n;return ((x-ox)*256,(y-oy)*256)
par=[px(*p) for p in json.load(open('EXTERNAL_tcad_parcel.geojson'))['features'][0]['geometry']['coordinates'][0]]
bld=[px(*p) for p in json.load(open('osm_bldg.json'))[0]['geojson']['coordinates'][0]]
im=Image.open('esri_z20.png').convert('RGB');W,H=im.size
def mask(poly):
    m=Image.new('L',(W,H),0);ImageDraw.Draw(m).polygon(poly,fill=1);return np.array(m,bool)
P=mask(par);B=mask(bld);O=P&~B
# depth axis: N edge = par[3]->par[0], S edge = par[1]->par[2]
nmid=np.mean([par[3],par[0]],0);smid=np.mean([par[1],par[2]],0)
ax=(smid-nmid)/np.linalg.norm(smid-nmid)
yy,xx=np.mgrid[0:H,0:W];proj=(xx-nmid[0])*ax[0]+(yy-nmid[1])*ax[1]
bproj=[(p[0]-nmid[0])*ax[0]+(p[1]-nmid[1])*ax[1] for p in bld]
bmin,bmax=min(bproj),max(bproj);depth=np.linalg.norm(smid-nmid)
REAR=O&(proj>bmax);FRONT=O&(proj<bmin);SIDE=O&~REAR&~FRONT
a=np.array(im).astype(float);r,g,b=a[...,0],a[...,1],a[...,2]
exg=2*g-r-b;bright=(r+g+b)/3
VEG=(exg>12)&(g>r)
SHADOW=bright<60
ft2=lambda m:m.sum()*mpp*mpp*10.7639
out={'m_per_px_z20_display':mpp,'m_per_px_z19_display':mpp*2,
'parcel_ft2':ft2(P),'bldg_ft2':ft2(B),'open_ft2':ft2(O),'rear_ft2':ft2(REAR),'front_ft2':ft2(FRONT),'side_ft2':ft2(SIDE),
'rear_depth_ft':(depth-bmax)*mpp*3.2808,'front_depth_ft':bmin*mpp*3.2808,'parcel_depth_ft':depth*mpp*3.2808}
for nm,M in [('open',O),('rear',REAR),('side',SIDE),('front',FRONT)]:
    out[nm+'_veg_frac']=float((VEG&M).sum()/M.sum());out[nm+'_shadow_frac']=float((SHADOW&M).sum()/M.sum())
for k,v in out.items(): print(k,round(v,3))
json.dump(out,open('numbers.json','w'),indent=1)
# annotate
ov=im.copy();d=ImageDraw.Draw(ov,'RGBA')
col=np.zeros((H,W,4),np.uint8)
col[REAR]=(255,0,0,90);col[SIDE]=(255,140,0,80);col[FRONT]=(0,120,255,80);col[VEG&O]=(0,255,0,110)
ov=Image.alpha_composite(ov.convert('RGBA'),Image.fromarray(col));d=ImageDraw.Draw(ov)
d.line(par,fill=(255,255,0),width=3);d.line(bld,fill=(0,255,255),width=2)
try: f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',16)
except: f=ImageFont.load_default()
cx,cy=999,953;x0,y0=cx-300,cy-300
# scale bar 30 ft
L=30/3.2808/mpp; sx,sy=x0+30,y0+560
d.rectangle((sx,sy,sx+L,sy+8),fill='white',outline='black');d.rectangle((sx,sy,sx+L/2,sy+8),fill='black')
d.text((sx,sy-22),'0      15     30 ft (%.1f m)'%(30/3.2808),fill='white',font=f,stroke_width=2,stroke_fill='black')
d.polygon([(x0+560,y0+60),(x0+550,y0+85),(x0+570,y0+85)],fill='white');d.text((x0+553,y0+35),'N',fill='white',font=f,stroke_width=2,stroke_fill='black')
lab=[('TCAD parcel 203610 (~6,700 ft2)',(255,255,0)),('OSM building footprint (~2,890 ft2)',(0,255,255)),('Rear yard (red)',(255,80,80)),('Side yards (orange)',(255,160,0)),('Front strip/parking (blue)',(80,160,255)),('Vegetation/canopy detected (green)',(0,255,0))]
for i,(t,c) in enumerate(lab): d.text((x0+10,y0+10+i*20),t,fill=c,font=f,stroke_width=2,stroke_fill='black')
d.text((x0+10,y0+575),'909 W 22nd St, Austin TX | Esri World Imagery (Nearmap 2023-10-08) | z20 = %.3f m/px display, ~%.2f m/px effective'%(mpp,mpp*2),fill='white',font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',11) if f!=ImageFont.load_default() else f,stroke_width=1,stroke_fill='black')
ov.crop((x0,y0,x0+600,y0+600)).convert('RGB').save('tke_backyard_annotated.png')
im.crop((x0,y0,x0+600,y0+600)).save('tke_lot_raw_z20.png')
# context
c2=Image.open('esri_z19.png').convert('RGB');d2=ImageDraw.Draw(c2)
par19=[(p[0]/2-(119786*2-ox)*128,p[1]/2-(215825*2-oy)*128) for p in par]
d2.line(par19,fill=(255,255,0),width=3)
L19=100/3.2808/(mpp*2);d2.rectangle((40,1230,40+L19,1240),fill='white',outline='black');d2.text((40,1205),'100 ft',fill='white',font=f,stroke_width=2,stroke_fill='black')
d2.text((40,20),'Context: TKE house parcel (yellow), 909 W 22nd St. N up. Esri/Nearmap 2023-10-08',fill='white',font=f,stroke_width=2,stroke_fill='black')
c2.save('tke_context_z19.png')
