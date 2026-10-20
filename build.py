from pathlib import Path
import json, html, re, shutil, unicodedata
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dist'
if OUT.exists(): shutil.rmtree(OUT)
OUT.mkdir()
source=(ROOT/'index.html').read_text(encoding='utf-8')
def esc(x): return html.escape(str(x or ''), quote=True)
def slug(x):
    x=unicodedata.normalize('NFKD',x).encode('ascii','ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+','-',x).strip('-') or 'materia'
def md(text):
    chunks=[]
    for line in str(text or '').splitlines():
        if not line.strip(): continue
        if line.startswith('### '): chunks.append('<h3>'+esc(line[4:])+'</h3>')
        elif line.startswith('## '): chunks.append('<h2>'+esc(line[3:])+'</h2>')
        elif line.startswith('# '): chunks.append('<h1>'+esc(line[2:])+'</h1>')
        else:
            s=esc(line)
            s=re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',s)
            s=re.sub(r'\*(.+?)\*',r'<em>\1</em>',s)
            chunks.append('<p>'+s+'</p>')
    return '\n'.join(chunks)
posts=[]
for path in sorted((ROOT/'content/materias').glob('*.json')):
    try: d=json.loads(path.read_text(encoding='utf-8'))
    except (ValueError, OSError): continue
    if d.get('status','').strip().lower()!='publicado': continue
    d['_slug']=slug(path.stem)
    posts.append(d)
posts.sort(key=lambda x: x.get('data',''), reverse=True)
cards=[]
for i,d in enumerate(posts):
    href='/materias/'+d['_slug']+'.html'
    cover=('<img src="'+esc(d['capa'])+'" alt="" style="width:100%;height:100%;object-fit:cover;position:absolute;inset:0">') if d.get('capa') else '<span class="artnum">'+str(i+1).zfill(2)+'</span><div class="shape"></div>'
    cards.append('<article class="card"><div class="art '+('rose' if i%3==1 else 'sand' if i%3==2 else '')+'">'+cover+'</div><div class="cardbody"><span class="category">'+esc(d.get('pilar'))+'</span><h3>'+esc(d.get('titulo'))+'</h3><p>'+esc(d.get('subtitulo'))+'</p><a class="read" href="'+href+'">Leia a matéria ↗</a></div></article>')
    article='''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'''+esc(d.get('titulo'))+''' — RENOVO</title><link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Manrope:wght@400;600&display=swap" rel="stylesheet"><style>body{margin:0;background:#F4EFE5;color:#30312E;font-family:Manrope,Arial,sans-serif}header{padding:23px max(24px,calc((100vw - 900px)/2));border-bottom:1px solid #29483B33}a{color:#29483B}header a{font:32px 'DM Serif Display',Georgia,serif;text-decoration:none}main{max-width:760px;margin:60px auto;padding:0 24px 90px}.kicker{color:#794451;text-transform:uppercase;letter-spacing:.16em;font-size:12px}h1,h2,h3{font-family:'DM Serif Display',Georgia,serif;color:#29483B}h1{font-size:clamp(42px,7vw,72px);line-height:1.05;margin:20px 0}h2{font-size:32px}p{font-size:17px;line-height:1.9}figure{margin:28px 0}figure img{width:100%;max-height:480px;object-fit:cover}.meta{font-size:13px;color:#794451;margin:24px 0 36px}.back{display:inline-block;margin-top:40px}</style></head><body><header><a href="/">RENOVO</a></header><main><div class="kicker">'''+esc(d.get('pilar'))+''' · Uma Revista Pulse Adolescentes</div><h1>'''+esc(d.get('titulo'))+'''</h1><p>'''+esc(d.get('subtitulo'))+'''</p><div class="meta">'''+esc(d.get('autora'))+' · '+esc(d.get('data'))+'''</div>'''+('<figure><img src="'+esc(d['capa'])+'" alt="Imagem de capa"></figure>' if d.get('capa') else '')+md(d.get('texto'))+'''<p><a class="back" href="/">← Voltar à revista</a></p></main></body></html>'''
    target=OUT/'materias'/ (d['_slug']+'.html')
    target.parent.mkdir(exist_ok=True)
    target.write_text(article,encoding='utf-8')
if cards:
    source=re.sub(r'(<div class="cards" id="cards">).*?(</div>\s*<div class="pillars")',lambda m:m.group(1)+''.join(cards)+m.group(2),source,count=1,flags=re.S)
    source=source.replace('Os textos desta demonstração ainda não representam uma edição publicada.','As matérias publicadas podem ser lidas na seção de destaque. A edição digital completa ainda está em desenvolvimento.')
source=source.replace('Protótipo inicial. Busca, formulário e textos de exemplo ainda não estão ligados a um sistema de publicação.','Site editorial RENOVO. A Carta RENOVO ainda não recebe inscrições.')
(OUT/'index.html').write_text(source,encoding='utf-8')
images=ROOT/'imagens'
if images.exists(): shutil.copytree(images,OUT/'imagens')
print(f'Build: {len(posts)} matéria(s) publicada(s).')
