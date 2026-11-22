#!/usr/bin/env python3
"""Create a portable interactive preview after running build_site.py.
Usage: python scripts/build_preview.py [--output /path/MCLab_Preview.html]
No external dependencies. Local photographs/figures are embedded.
"""
import argparse,base64,json,mimetypes,re
from pathlib import Path
from urllib.parse import unquote, urlsplit
ROOT=Path(__file__).resolve().parents[1]

def inline_preview_assets(html,css):
    """Inline the current stylesheet and remove external copies of inlined scripts."""
    def local_asset(tag,attribute):
        match=re.search(r'(?<![\w:-])'+attribute+r'\s*=\s*(["\'])(.*?)\1',tag,re.I|re.S)
        if not match:return ''
        url=urlsplit(match[2])
        return url.path if not url.scheme and not url.netloc else ''
    css_inlined=False
    def stylesheet(match):
        nonlocal css_inlined
        if local_asset(match[0],'href')!='assets/css/style.css':return match[0]
        if css_inlined:return ''
        css_inlined=True
        return '<style>\n'+css+'\n</style>'
    html=re.sub(r'<link\b[^>]*>',stylesheet,html,flags=re.I)
    def script(match):
        opening=match[0].split('>',1)[0]
        return '' if local_asset(opening,'src') in ('data/site-data.js','assets/js/app.js') else match[0]
    return re.sub(r'<script\b[^>]*>[\s\S]*?</script\s*>',script,html,flags=re.I)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,default=ROOT/'MCLab_Preview.html')
    args=ap.parse_args();site=ROOT/'_site'
    if not (site/'data/site-data.js').is_file():raise SystemExit('Run python scripts/build_site.py first.')
    text=(site/'data/site-data.js').read_text(encoding='utf-8')
    data=json.loads(re.search(r'window.MCLAB_DATA\s*=\s*(\{[\s\S]*\})\s*;',text).group(1))
    def embed(obj):
        if isinstance(obj,dict):
            for key,value in list(obj.items()):
                if key in ('image','photo','heroImage') and isinstance(value,str) and value and not value.startswith(('http:','https:','data:')):
                    path=(site/unquote(value)).resolve()
                    if path.is_relative_to(site.resolve()) and path.is_file():
                        mime=mimetypes.guess_type(path.name)[0]
                        if mime in ('image/jpeg','image/png','image/webp'):obj[key]='data:'+mime+';base64,'+base64.b64encode(path.read_bytes()).decode()
                else:embed(value)
        elif isinstance(obj,list):
            for value in obj:embed(value)
    embed(data)
    html=(site/'index.html').read_text(encoding='utf-8')
    css=(site/'assets/css/style.css').read_text(encoding='utf-8');js=(site/'assets/js/app.js').read_text(encoding='utf-8')
    html=inline_preview_assets(html,css)
    favicon=base64.b64encode((site/'assets/images/favicon.svg').read_bytes()).decode()
    html=html.replace('assets/images/favicon.svg','data:image/svg+xml;base64,'+favicon)
    payload='window.MCLAB_SINGLE_PREVIEW=true;\nwindow.MCLAB_DATA='+json.dumps(data,ensure_ascii=False).replace('<','\\u003c')+';'
    html=html.replace('</body>','<script>'+payload+'</script>\n<script>'+js.replace('</script','<\\/script')+'</script>\n</body>')
    args.output.write_text(html,encoding='utf-8');print(args.output)
if __name__=='__main__':main()
