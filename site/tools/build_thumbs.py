import zipfile, io, re, os
from PIL import Image
T=128; L='/mnt/project-files/launch/'
img={}
z=zipfile.ZipFile(L+'final-backup-2026-11-20/claysons-images-small.zip')
for n in z.namelist():
    m=re.search(r'(\d+)\.jpg$',n)
    if m: img[int(m.group(1))]=(z,n)
z2=zipfile.ZipFile(L+'post-reveal-audit-2026-11-25/claysons-edits-FINAL-184.zip'); c=0
for n in z2.namelist():
    m=re.search(r'images/(\d+)\.png$',n)
    if m: img[int(m.group(1))]=(z2,n); c+=1
print('overrides',c,len(img))
os.makedirs('site/world/img/thumbs',exist_ok=True)
for s in range(13):
    sh=Image.new('RGB',(T*10,T*10))
    for k in range(100):
        i=s*100+k+1; zz,n=img[i]
        im=Image.open(io.BytesIO(zz.read(n))).convert('RGB').resize((T,T),Image.LANCZOS)
        sh.paste(im,((k%10)*T,(k//10)*T))
    sh.save(f'site/world/img/thumbs/s{s}.jpg',quality=80)
