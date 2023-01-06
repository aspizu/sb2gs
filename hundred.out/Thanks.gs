globals cam_x, cam_y, zoom, target_zoom, cam_ay, cam_ayc, cam_ays, last_z, DEBUG;
listglobals ;
costumes "thank you.svg", "100000.svg";

onflag {
  hide;
}

on "celebrate" {
  gotofront;
  setghosteffect 100;
  show;
  goto 0, 0;
  repeat 50 {
    changeghosteffect -2;
  }
}

on "tick - front" {
  gotofront;
}

