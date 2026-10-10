from pathlib import Path
import json,re
root=Path(__file__).resolve().parent.parent
html=(root/'index.html').read_text()
css=(root/'src/style.css').read_text();css=re.sub(r'^@import[^\n]*\n','',css,flags=re.M)
js='\n'.join((root/p).read_text() for p in ['src/worlds.mjs','src/core.mjs','src/app.mjs'])
js=re.sub(r'^import .*?;\s*$', '',js,flags=re.M)
js=re.sub(r'\bexport\s+(?=(?:const|function|class)\b)', '',js)
summary=json.loads((root/'evidence/summary.json').read_text())
js=js.replace("fetch('./evidence/summary.json')",'Promise.resolve({json:async()=>('+json.dumps(summary)+')})')
html=html.replace('<link rel="stylesheet" href="./src/style.css"/>','<style>'+css+'</style>')
html=html.replace('<script type="module" src="./src/app.mjs"></script>','<script>'+js+'</script>')
(root/'standalone.html').write_text(html)
print('standalone.html', len(html),'bytes')
