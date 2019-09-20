precision mediump float;
precision mediump sampler2D;

uniform sampler2D tex;
uniform vec2 lightpos[14];
uniform vec3 lightcolor[14];

uniform vec2 screensize;

//const vec2 screen = vec2(1024.0, 768.0);
const float drawscale = 1.0;
const float distscale = 3.0;

void main(){
  vec2 coords = (gl_FragCoord.xy * 2.0 + 1.0)/(screensize*2.0);
  vec4 point = texture2D(tex, coords*drawscale);

  vec3 col = vec3(0.0);
  for (int i=0; i<14; i++) {
    col = max(col, lightcolor[i]*(1.0-distance(coords, lightpos[i])*distscale));
  }
  point.rgb *= col;
  point.a = 1.0;
  gl_FragColor = point;
}
