globals cam_x, cam_y, zoom, target_zoom, cam_ay, cam_ayc, cam_ays, last_z, DEBUG;
listglobals ;
costumes "blank.svg", "user.svg", "user2.svg", "user3.svg", "user4.svg", "user5.svg", "user6.svg", "user7.svg", "user8.svg", "user9.svg", "user10.svg", "user11.svg", "user12.svg", "user13.svg";

on "Setup" {
  costume = "";
  hide;
  switchcostume "blank";
}

on "tick - draw" {
  if gt(costume, "") {
    if eq(costume(), 1) {
      switchcostume costume;
      show;
    }
    pos_3d sub(x, cam_x), sub(y, cam_y), z;
  } else {
    wait 0;
  }
}

def position x, y {
  goto $x, $y;
}

nowarp def spawn costume, x, y, s {
  costume = $costume;
  x = $x;
  y = $y;
  z = $s;
  s = 75;
  sy = 0;
  cloneself ;
  costume = "";
}

def pos_3d x, y, z {
  posPerp sub(mul($x, cam_ayc), mul($z, cam_ays)), $y, add(mul($z, cam_ayc), mul($x, cam_ays));
}

def posPerp x, y, z {
  m = div(800, add($z, 800));
  t = mul(m, mul(s, zoom));
  setsize mul(t, 3);
  position round(mul(mul($x, zoom), m)), round(mul(mul($y, zoom), m));
  setsize t;
  setbrightnesseffect sub(20, mul(0.3, t));
  setghosteffect sy;
  thisZ = $z;
  order;
}

on "celebrate" {
  celebrate;
}

nowarp def spawn_c a, y, d {
  spawn random(2, 14), add(300, mul($d, sin($a))), random(200, 700), mul($d, cos($a));
}

on "tick - move" {
  if lt(y, -35) {
    if lt(sy, 100) {
      sy += 1;
    } else {
      sy = 0;
      y = 480;
    }
  } else {
    y += -2;
  }
}

def celebrate  {
  repeat 30 {
    spawn_c random(0, 359), random(-50, 600), random(200, 600);
  }
}

on "tick - order" {
  order;
}

def order  {
  if gt(last_z, thisZ) {
    goforward 1;
  }
  last_z = thisZ;
}

