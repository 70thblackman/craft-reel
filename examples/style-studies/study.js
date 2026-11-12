// Two short silent studies using the unchanged engine. No narration, W() or SFX.
// Static markup below is authored here; plain copy is assigned with textContent.
const studyTf = (n,o=1,x=0,y=0,s=1,r=0) => {
  n.style.opacity=o.toFixed(4);
  n.style.transform=`translate3d(${x.toFixed(2)}px,${y.toFixed(2)}px,0) scale(${s.toFixed(4)}) rotate(${r.toFixed(2)}deg)`;
};
const collage = document.body.dataset.style === 'collage';
scene(0, DURATION + .1, 'study', (cam) => {
  const root = at(cam, `<div class="study ${collage ? 'collage' : 'minimal'}"></div>`);
  const tag = at(root, '<p class="eyebrow"></p>');
  tag.textContent = collage ? 'CRAFT REEL / COLLAGE STUDY' : 'CRAFT REEL / A QUIETER RHYTHM';
  if (!collage) {
    const rule = at(root, '<div class="rule"></div>');
    const title = at(root, '<h1 lang="fa" dir="rtl"></h1>');
    title.textContent = 'از ایده تا حرکت';
    const english = at(root, '<p class="english" lang="en" dir="ltr"></p>');
    english.textContent = 'FROM IDEA TO MOTION';
    const note = at(root, '<p class="note" lang="fa" dir="rtl"></p>');
    note.textContent = 'یک ایده، با ریتمی آرام‌تر';
    return (t) => {
      rule.style.transform = `scaleY(${E.out(P(t,.15,1.2))})`;
      studyTf(title,E.out(P(t,.4,1.3)),0,(1-E.out(P(t,.4,1.3)))*35);
      studyTf(english,E.out(P(t,1,1.8)),0,(1-E.out(P(t,1,1.8)))*20);
      studyTf(note,E.out(P(t,1.7,2.4)));
    };
  }
  const disk = at(root, '<div class="disk"></div>');
  const image = document.createElement('img');
  image.className='photo'; image.alt='Original illustrative landscape, not stock photography';
  image.src='sample-landscape.svg'; root.appendChild(image);
  const tape = at(root, '<div class="tape"></div>');
  const title = at(root, '<h1 lang="en" dir="ltr"></h1>');
  title.textContent = 'A different perspective.';
  const label = at(root, '<p class="label"></p>'); label.textContent='MAKE ROOM FOR IDEAS';
  const foot = at(root, '<p class="foot"></p>'); foot.textContent='Original illustration / Replace with your own image';
  return (t) => {
    studyTf(disk,E.out(P(t,0,.7)),0,0,.92+.08*E.out(P(t,0,.7)));
    const p=E.out(P(t,.2,1.2)); studyTf(image,p,(1-p)*-90,(1-p)*50,1,-5);
    studyTf(tape,E.out(P(t,.8,1.15)),0,0,1,-9);
    studyTf(title,E.out(P(t,1,1.8)),0,(1-E.out(P(t,1,1.8)))*50);
    studyTf(label,E.out(P(t,1.7,2.1)),0,0,1,3);
    studyTf(foot,E.out(P(t,2,2.5)));
  };
}, {push:0,tr:'cut',quiet:true,hits:[]});

// Extend actual asset readiness without changing the shared engine.
const engineReady = window.ready;
window.ready = engineReady.then(async()=>{
  await document.fonts.ready;
  await Promise.all([...document.images].map(im=>im.decode()));
});
const engineSeek = window.seek;
window.seek = async(t)=>{await window.ready;await engineSeek(t);};
window.ready.then(()=>window.seek(3)); // settled preview when opening the file
