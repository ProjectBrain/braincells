attribute vec3 vertex;

void main(){
    //vertex.x += 0.001;
    gl_Position.xyz = vertex;
    gl_Position.w = 1.0;
}
