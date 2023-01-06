globals cam_x, cam_y, zoom, target_zoom, cam_ay, cam_ayc, cam_ays, last_z, DEBUG;
listglobals ;
costumes "costume1.svg", "costume2.svg";

onflag {
  DEBUG = 0;
  cam_x = -200;
  cam_y = 0;
  zoom = 0.6;
  cam_sx = 0;
  cam_ay = 0;
  broadcast "Setup";
  forever {
    cam_ays = sin(cam_ay);
    cam_ayc = cos(cam_ay);
    broadcast "tick - move";
    broadcast "tick - draw";
    broadcast "tick - order 2";
    last_z = 0;
  }
}

on "Setup" {
  cam_x = -600;
  cam_y = 0;
  zoom = 2;
  repeat 115 {
    zoom += mul(sub(0.5, zoom), 0.04);
  }
  repeat 40 {
    zoom += mul(sub(0.5, zoom), 0.1);
    cam_x += mul(sub(300, cam_x), 0.1);
  }
  cam_sx = 0;
  broadcast "celebrate";
  repeat 80 {
    cam_ay += cam_sx;
    if lt(cam_sx, 3) {
      cam_sx += 0.2;
    }
    if lt(cam_ay, 45) {
      cam_y += 5;
    }
  }
  forever {
    cam_ay += cam_sx;
  }
}

def change cx, mx {
  if gt(abs($cx), $mx) {
    cam_x += mul($mx, div($cx, abs($cx)));
  } else {
    cam_x += $cx;
  }
}

on "tick - order 2" {
  broadcast "tick - order";
  broadcast "tick - front";
}

on "Setup" {
  forever {
    playsound ;
  }
}

