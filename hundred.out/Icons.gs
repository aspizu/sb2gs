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
  } else {
    wait ;
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

def pos x, y, z {
}

def posPerp x, y, z {
  m = div(800, add($z, 800));
  t = mul(m, mul(s, zoom));
  setsize mul(t, 3);
}

on "celebrate" {
}

nowarp def spawn a, y, d {
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
  }
}

on "tick - order" {
}

def order  {
  if gt(last_z, thisZ) {
    goforward 1;
  }
  last_z = thisZ;
}

