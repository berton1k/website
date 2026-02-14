
document.addEventListener("DOMContentLoaded", () => {

  const cursor = document.getElementById("custom-cursor");
  const canvas = document.getElementById("particle-canvas");

  if (!cursor || !canvas) return;

  const ctx = canvas.getContext("2d");

  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;

  let particles = [];
  let mouse = { x: 0, y: 0 };
  let prevMouse = { x: 0, y: 0 };

  document.addEventListener("mousemove", e => {
    prevMouse.x = mouse.x;
    prevMouse.y = mouse.y;

    mouse.x = e.clientX;
    mouse.y = e.clientY;

    cursor.style.left = mouse.x + "px";
    cursor.style.top = mouse.y + "px";

    const dx = mouse.x - prevMouse.x;
    const dy = mouse.y - prevMouse.y;

    for (let i = 0; i < 6; i++) {
      particles.push(new Particle(
        mouse.x,
        mouse.y,
        -dx,
        -dy
      ));
    }
  });

  class Particle {
    constructor(x, y, vx, vy) {
      this.x = x;
      this.y = y;
      this.vx = vx * 0.3 + (Math.random() - 0.5) * 2;
      this.vy = vy * 0.3 + (Math.random() - 0.5) * 2;
      this.life = 1;
      this.size = Math.random() * 3 + 1;
    }

    update() {
      this.x += this.vx;
      this.y += this.vy;
      this.life -= 0.03;
    }

    draw() {
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(0, 180, 255, ${this.life})`;
      ctx.shadowBlur = 15;
      ctx.shadowColor = "rgba(0,180,255,1)";
      ctx.fill();
    }
  }

  function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    particles = particles.filter(p => p.life > 0);

    particles.forEach(p => {
      p.update();
      p.draw();
    });

    requestAnimationFrame(animate);
  }

  animate();

  window.addEventListener("resize", () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  });

});

document.addEventListener("DOMContentLoaded", () => {

  const canvas = document.getElementById("snow-canvas");
  if (!canvas) return;

  const ctx = canvas.getContext("2d");

  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;

  const snowflakes = [];
  const SNOW_COUNT = 150;

  class Snowflake {
    constructor() {
      this.reset();
      this.y = Math.random() * canvas.height;
    }

    reset() {
      this.x = Math.random() * canvas.width;
      this.y = -10;
      this.radius = Math.random() * 2.5 + 0.5;
      this.speed = Math.random() * 1 + 0.5;
      this.wind = Math.random() * 0.6 - 0.3;
      this.alpha = Math.random() * 0.5 + 0.3;
    }

    update() {
      this.y += this.speed;
      this.x += this.wind;

      if (this.y > canvas.height) {
        this.reset();
      }
    }

    draw() {
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(255,255,255,${this.alpha})`;
      ctx.fill();
    }
  }

  for (let i = 0; i < SNOW_COUNT; i++) {
    snowflakes.push(new Snowflake());
  }

  function animateSnow() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    snowflakes.forEach(s => {
      s.update();
      s.draw();
    });

    requestAnimationFrame(animateSnow);
  }

  animateSnow();

  window.addEventListener("resize", () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  });

});

document.addEventListener("DOMContentLoaded", () => {
  const menu = document.querySelector(".side-menu");
  const zone = document.querySelector(".menu-hover-zone");

  if (!menu || !zone) return;

  let isInsideMenu = false;

  zone.addEventListener("mouseenter", () => {
    menu.classList.add("open");
  });

  menu.addEventListener("mouseenter", () => {
    isInsideMenu = true;
    menu.classList.add("open");
  });

  menu.addEventListener("mouseleave", () => {
    isInsideMenu = false;
    menu.classList.remove("open");
  });

  zone.addEventListener("mouseleave", () => {
    if (!isInsideMenu) {
      menu.classList.remove("open");
    }
  });
});

