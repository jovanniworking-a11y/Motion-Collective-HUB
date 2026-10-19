import subprocess, numpy as np, re, sys
v=sys.argv[1]; W,H=270,480
raw=subprocess.run(['ffmpeg','-v','error','-i',v,'-vf',f'scale={W}:{H}','-f','rawvideo','-pix_fmt','gray','-'],capture_output=True).stdout
F=np.frombuffer(raw,np.uint8).reshape(-1,H,W).astype(np.float32)
mean=F.mean((1,2)); white=(F>=250).mean((1,2)); diff=np.r_[0,np.abs(np.diff(F,axis=0)).mean((1,2))]
cl=[l for l in open(sys.argv[2]) if l.startswith('| ') and ' s |' in l]
cuts=[float(re.match(r'\| ([\d.]+) s',l).group(1)) for l in cl]; cutf=[int(round(c*30)) for c in cuts]
blown=[i for i in range(len(F)) if white[i]>.12]; print('blown frames:',len(blown), [f'{i/30:.1f}' for i in blown[::5]])
fl=[i for i in range(2,len(F)-1) if diff[i]>max(18,3*np.median(diff[max(0,i-8):i+8])) and not any(abs(i-c)<=1 for c in cutf)]
print('flash/jump frames:',[f'{i/30:.2f}' for i in fl])
dips=[i for i in range(2,len(F)-2) if (mean[i-2]+mean[i+2])/2>30 and mean[i]<.65*(mean[i-2]+mean[i+2])/2 and not any(abs(i-c)<=2 for c in cutf)]
print('exposure dips:',len(dips),[f'{i/30:.2f}' for i in dips])
