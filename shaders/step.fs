precision mediump float;
precision mediump sampler2D;

uniform sampler2D tex;
uniform vec2 texsize;

float valAtOffset(vec2 xy) {
  return texture2D(tex, ((gl_FragCoord.xy + xy) * 2.0 + 1.0)/(texsize*2.0)).r;
}

void main(){
  float me = valAtOffset(vec2(0.0, 0.0));
  float up = valAtOffset(vec2(0.0, 1.0));
  float dn = valAtOffset(vec2(0.0, -1.0));
  float lf = valAtOffset(vec2(-1.0, 0.0));
  float rt = valAtOffset(vec2(1.0, 0.0));
  float ul = valAtOffset(vec2(1.0, -1.0));
  float ur = valAtOffset(vec2(1.0, 1.0));
  float dl = valAtOffset(vec2(-1.0, -1.0));
  float dr = valAtOffset(vec2(-1.0, 1.0));

  float sum = up+dn+lf+rt+ul+ur+dl+dr;
  float avg = sum / 8.0;

//  if (sum >= 2.1) me = avg * 0.999;
//  else if (sum <= 1.0) me = min(1.0, me * 1.03);
//  else me = min((me + 0.21) * (me + 0.21), 1.0);

  if (avg > me + 0.001) me = pow(avg, 0.99) * 0.995;
  else if (me > avg + 0.001) me = pow(me, 1.25) * 0.995;
  else me = 1.0;


  gl_FragColor.rgb = vec3(me);

}
