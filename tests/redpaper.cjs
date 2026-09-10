const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const source = fs.readFileSync(__dirname+'/../Scripts/Surge/RedPaperSurge.js','utf8');
const moduleText = fs.readFileSync(__dirname+'/../Surge/Modules/RedPaper_remove_ads.sgmodule','utf8');
const rules = [...moduleText.matchAll(/pattern=(.*?), requires-body/g)].map(m=>new RegExp(m[1]));
let count = 0;
function run(path, body, store = {}) {
 const url = 'https://edith.xiaohongshu.com/api/sns'+path;
 assert.equal(rules.filter(r=>r.test(url)).length,1, 'Exactly one rule must match '+path);
 let calls = [];
 vm.runInNewContext(source, {$request:{url},$response:{body:typeof body==='string'?body:JSON.stringify(body)},$persistentStore:{read:k=>store[k]??null,write:(v,k)=>(store[k]=v,true)},$done:x=>calls.push(x),console:{log(){}}},{timeout:1000});
 assert.equal(calls.length,1);
 count++;
 return calls[0].body ? JSON.parse(calls[0].body) : null;
}
for(const p of ['/v1/note/imagefeed','/v2/note/feed']) {
 const r=run(p,{data:[{note_list:[{media_save_config:{disable_save:true,disable_watermark:false}}]}]});
 assert.equal(r.data[0].note_list[0].media_save_config.disable_watermark,true);
}
assert.equal(run('/v3/note/videofeed',{data:[{media_save_config:{disable_watermark:false}}]}).data[0].media_save_config.disable_watermark,true);
const store={redBookVideoFeedUnlock:'broken json'};
const note={model_type:'note',id:'n1',video_info_v2:{media:{stream:{h265:[{master_url:'https://media.example/clean.mp4'}]}}}};
assert.deepEqual(run('/v4/note/videofeed',{data:[{model_type:'note',ad:{}},note]},store).data,[note]);
assert.equal(run('/v10/note/video/save',{data:{note_id:'n1',download_url:'watermarked'}},store).data.download_url,'https://media.example/clean.mp4');
assert.deepEqual(run('/v4/note/videofeed',{data:[{model_type:'note',ad:{}}]}).data,[]);
assert.deepEqual(run('/v6/homefeed?',{data:[{id:1,ads_info:{}},{id:2}]}).data,[{id:2}]);
assert.deepEqual(run('/v10/search/notes?',{data:{items:[{model_type:'ad'},{model_type:'note'}]}}).data.items,[{model_type:'note'}]);
assert.deepEqual(run('/v1/search/banner_list',{code:0,data:{ad:1}}),{code:0,data:{}});
assert.deepEqual(run('/v1/search/hot_list',{data:{items:[1],keep:1}}).data,{items:[],keep:1});
assert.deepEqual(run('/v4/search/hint',{data:{hint_words:[1]}}).data.hint_words,[]);
assert.deepEqual(run('/v4/search/trending?',{data:{queries:[1],hint_word:{a:1},keep:1}}).data,{queries:[],hint_word:{},keep:1});
assert.deepEqual(run('/v1/system_service/config?',{data:{splash:{},app_theme:{},keep:1}}).data,{keep:1});
assert.equal(run('/v2/system_service/splash_config',{data:{ads_groups:[{start_time:0,ads:[{start_time:0}]}]}}).data.ads_groups[0].ads[0].start_time,3818332800);
const liveStore={};
run('/v1/note/imagefeed',{data:[{note_list:[{images_list:[{live_photo_file_id:'f1',live_photo:{media:{video_id:'v1',stream:{h265:[{master_url:'https://media.example/live.mp4'}]}}}}]}]}]},liveStore);
assert.equal(run('/v1/note/live_photo/save',{data:{datas:[{file_id:'f1',url:'https://media.example/watermarked.mp4'}]}},liveStore).data.datas[0].url,'https://media.example/live.mp4');
const commentStore={};
run('/v5/note/comment/list',{data:{comments:[{note_id:'n1',pictures:[{video_id:'v2',video_info:JSON.stringify({stream:{h265:[{master_url:'https://media.example/comment.mp4'}]}})}]}]}},commentStore);
assert.equal(run('/v1/interaction/comment/video/download',{data:{video:{video_id:'v2',video_url:'watermarked'}}},commentStore).data.video.video_url,'https://media.example/comment.mp4');
assert.equal(run('/v1/note/imagefeed',''),null);
assert.equal(run('/v1/note/imagefeed','<html>error</html>'),null);
assert.equal(run('/v1/note/imagefeed','null'),null);
assert.equal(rules.length,16);
assert(!moduleText.includes('[MitM]')&&!moduleText.includes('[Rewrite]'));
assert(moduleText.includes('hostname = %APPEND%'));
assert.equal(moduleText.split('\n').filter(x=>x.includes('data-type=')).length,5);
console.log(`${count} mocked-response checks passed; 16 script patterns and 5 Map Local rules checked.`);
