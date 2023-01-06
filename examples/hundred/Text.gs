globals cam_x, cam_y, zoom, target_zoom, cam_ay, cam_ayc, cam_ays, last_z, DEBUG;
listglobals ;
costumes "blank.svg", "n1.svg", "_n1.png", "_n1b.png", "n0.svg", "_n0.png", "_n0b.png", "comma.svg", "followers.svg", "follo.svg", "wers!.svg";

on "Setup" {
  costume = "";
  jt = 0;
  hide;
  switchcostume "blank";
  wait 0.4;
  spawn "n1", 0, 280, 210;
  wait 0.2;
  spawn "n0", 85, 280, 210;
  wait 0.2;
  spawn "n0", 195, 280, 210;
  wait 0.2;
  spawn "comma", 275, 280, 210;
  wait 0.2;
  spawn "n0", 355, 280, 210;
  wait 0.2;
  spawn "n0", 465, 280, 210;
  wait 0.2;
  spawn "n0", 575, 280, 210;
}

on "tick - move" {
  if gt(costume, "") {
    sy += -2;
    y += sy;
    if lt(y, 0) {
      y = 0;
      jt += 1;
      if gt(jt, 60) {
        sy = 20;
        jt = 0;
      } else {
        if lt(sy, -15) {
          sound = "s1";
        } else {
          if lt(sy, -7) {
            sound = "s2";
          }
        }
        sy = floor(mul(sy, -0.5));
      }
    }
  }
}

on "tick - draw" {
  if gt(costume, "") {
    if eq(costume(), 1) {
      switchcostume costume;
      show;
      if eq(letter(1, costumename()), "_") {
        setghosteffect 50;
      }
    }
    if eq(letter(1, costumename()), "_") {
      setghosteffect add(div(y, 2), 85);
      pos_3d sub(x, cam_x), sub(sub(-158, y), cam_y);
    } else {
      pos_3d sub(x, cam_x), sub(y, cam_y);
    }
    if gt(sound, "") {
      startsound sound;
      sound = "";
    }
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
  s = $s;
  sy = 0;
  cloneself ;
  costume = join("_", $costume);
  x = $x;
  y = $y;
  s = $s;
  sy = 0;
  cloneself ;
  costume = "";
}

def pos_3d x, y {
  posPerp sub(mul($x, cam_ayc), mul(0, cam_ays)), $y, add(mul(0, cam_ayc), mul($x, cam_ays));
}

def posPerp x, y, z {
  m = div(800, add($z, 800));
  setsize mul(mul(m, mul(s, zoom)), 2);
  position round(mul(mul($x, zoom), m)), round(mul(mul($y, zoom), m));
  setsize mul(m, mul(s, zoom));
  thisZ = $z;
  order;
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

