import {execFileSync} from 'node:child_process';
import {catalog} from './catalog.mjs';
import {createHash} from 'node:crypto';
import {readFile} from 'node:fs/promises';
const git=(...args)=>execFileSync('git',args,{encoding:'utf8',stdio:['ignore','pipe','pipe']}).trim();
let previous='',stable=0,published='';
async function publish(){const items=await catalog();const hash=createHash('sha256');for(const a of items){hash.update(a.path);hash.update(await readFile('public/'+decodeURIComponent(a.path)))}const current=hash.digest('hex');if(process.argv.includes('--watch')){if(current!==previous){previous=current;stable=0;return}if(++stable<3||current===published)return}git('remote','get-url','lab');if(git('diff','--cached','--name-only'))throw Error('기존 staged 변경사항이 있습니다. 먼저 처리해 주세요.');git('add','--','public/assets','public/catalog.json');if(git('diff','--cached','--name-only'))git('commit','-m','Publish lab artifacts');git('push','lab','HEAD:main');published=current;console.log(new Date().toISOString(),'Assets synchronized');}
if(process.argv.includes('--watch')){console.log('Watching public/assets; files must remain stable for 30 seconds. Ctrl+C to stop.');for(;;){try{await publish()}catch(e){console.error(e.message)}await new Promise(r=>setTimeout(r,10000))}}else await publish();
