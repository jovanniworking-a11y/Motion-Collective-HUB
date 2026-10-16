from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader","--allow-file-access-from-files"]); pg=b.new_page(); L=[]
    pg.on("pageerror",lambda e:L.append(str(e))); pg.on("console",lambda m:L.append(m.type+' '+m.text) if m.type=='error' else None)
    pg.goto("file:///home/claude/motion/studio/_test.html"); pg.wait_for_timeout(8000); print(L[:5]); b.close()
