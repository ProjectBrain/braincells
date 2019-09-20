//#version 330 compatibility
//out vec3 color;

uniform sampler2D tex;
uniform vec2 texsize;
const vec2 texsize2 = vec2(1024.0, 768.0);
//const float texscale = 1.0/8.0;

vec4 texAtOffset(vec2 xy) {
  //return texture2D(tex, ((gl_FragCoord.xy + xy) * 2.0 + 1.0)/(screen*texscale*2.0));
  return texture2D(tex, ((gl_FragCoord.xy + xy) * 2.0 + 1.0)/(texsize*2.0));
}
 
void main(){
  vec4 centre = texAtOffset(vec2(0.0, 0.0));
  vec4 up = texAtOffset(vec2(0.0, 1.0)); 
  vec4 down = texAtOffset(vec2(0.0, -1.0));
  vec4 left = texAtOffset(vec2(-1.0, 0.0));
  vec4 right = texAtOffset(vec2(1.0, 0.0));
  vec4 upleft = texAtOffset(vec2(1.0, -1.0));
  vec4 upright = texAtOffset(vec2(1.0, 1.0));
  vec4 downleft = texAtOffset(vec2(-1.0, -1.0));
  vec4 downright = texAtOffset(vec2(-1.0, 1.0));
  vec4 vout;

  float val = up.r + left.r + right.r + down.r + upleft.r + upright.r + downleft.r + downright.r;
  if (val > 3.0)
    vout.r = 0.0; //(0.0)/8.0; //(centre.r + (8.0-val)) / 9.0;
  else if (val < 2.0)
    vout.r = 0.0; //(centre.r + (0.0)) / 9.0;
  else
    vout.r = 1.0; //8.0/8.0; //(centre.r + (8.0)) / 9.0;
    
  vout.g = vout.r;
  vout.b = vout.r;

  vout.a = 1.0;
  gl_FragColor = vout;

}
