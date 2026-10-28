import { chromium } from 'playwright';
import { readFileSync, writeFileSync, readdirSync } from 'fs';
import { join } from 'path';

const dir = process.argv[2];
const names = readdirSync(dir).filter(f => f.endsWith('.mmd')).sort();

const b = await chromium.launch({ executablePath: process.env.CHROME });
const p = await (await b.newContext({ viewport:{width:1600,height:1200}, deviceScaleFactor:2 })).newPage();

await p.setContent(`<!doctype html><html><head><meta charset="utf-8">
<style>
  html,body{margin:0;padding:0;background:#fff;}
  #stage{display:inline-block;background:#fff;padding:26px 30px;}
  /* JetBrains Mono is not installed here; the stack falls through to the
     same ui-monospace the page uses, so the PNG matches the surrounding type. */
  svg{background:#fff !important;}
</style></head><body><div id="stage"></div></body></html>`);

await p.addScriptTag({ url: 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js' });
await p.waitForFunction(() => window.mermaid);

for (const f of names) {
  const src = readFileSync(join(dir,f),'utf8');
  const ok = await p.evaluate(async ({src}) => {
    const stage = document.getElementById('stage');
    stage.innerHTML = '';
    window.mermaid.initialize({
      startOnLoad:false, theme:'base', securityLevel:'loose',
      themeVariables:{
        background:'#ffffff', mainBkg:'#F3F0E9', primaryColor:'#F3F0E9',
        primaryTextColor:'#211C18', primaryBorderColor:'#B8B0A2',
        nodeBorder:'#B8B0A2', lineColor:'#5C5349', textColor:'#211C18',
        actorBkg:'#F3F0E9', actorBorder:'#8C8375', actorTextColor:'#211C18',
        actorLineColor:'#B8B0A2', signalColor:'#3B342D', signalTextColor:'#211C18',
        labelBoxBkgColor:'#F3F0E9', labelBoxBorderColor:'#B8B0A2', labelTextColor:'#211C18',
        loopTextColor:'#211C18', noteBkgColor:'#FBF3DD', noteTextColor:'#211C18',
        noteBorderColor:'#C9A94B', sequenceNumberColor:'#ffffff',
        fontFamily:'ui-monospace, SFMono-Regular, Menlo, Consolas, monospace',
        fontSize:'14px'
      },
      sequence:{
        useMaxWidth:false, mirrorActors:false, wrap:true, width:215,
        noteAlign:'left', noteMargin:12, messageAlign:'center',
        boxMargin:10, actorMargin:44, messageFontSize:13, noteFontSize:13,
        actorFontSize:13, actorFontWeight:600, diagramMarginX:16, diagramMarginY:12
      }
    });
    const { svg } = await window.mermaid.render('g'+Math.floor(performance.now()), src);
    stage.innerHTML = svg;
    const el = stage.querySelector('svg');
    el.removeAttribute('style');
    el.style.background = '#fff';
    return { w: el.getBoundingClientRect().width, h: el.getBoundingClientRect().height };
  }, { src });
  const png = f.replace(/\.mmd$/, '.png');
  await (await p.$('#stage')).screenshot({ path: join(dir,png) });
  console.log(png, JSON.stringify(ok));
}
await b.close();
