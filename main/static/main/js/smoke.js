const canvas = document.createElement('canvas');
canvas.className = 'smoke-canvas';
document.body.appendChild(canvas);

const ctx = canvas.getContext('2d');
let w, h;
const clouds = [];

function resize() {
  w = canvas.width = window.innerWidth;
  h = canvas.height = window.innerHeight;
}
window.addEventListener('resize', resize);
resize();

for (let i = 0; i < 40; i++) {
  clouds.push({
    x: Math.random() * w,
    y: Math.random() * h,
    r: 200 + Math.random() * 300,
    dx: 0.1 + Math.random() * 0.3,
    dy: 0.05 + Math.random() * 0.2,
    a: 0.03
  });
}

function draw() {
  ctx.clearRect(0, 0, w, h);
  clouds.forEach(c => {
    c.x += c.dx;
    c.y += c.dy;
    if (c.x - c.r > w) c.x = -c.r;
    if (c.y - c.r > h) c.y = -c.r;

    const g = ctx.createRadialGradient(c.x, c.y, 0, c.x, c.y, c.r);
    g.addColorStop(0, `rgba(255,255,255,${c.a})`);
    g.addColorStop(1, 'rgba(255,255,255,0)');
    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.arc(c.x, c.y, c.r, 0, Math.PI * 2);
    ctx.fill();
  });
  requestAnimationFrame(draw);
}
draw();
