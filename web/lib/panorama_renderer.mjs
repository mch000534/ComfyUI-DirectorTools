import { cameraAngles } from './geometry.mjs?v=0.8.3';

const VERTEX = `#version 300 es
void main() {
    vec2 p = gl_VertexID == 0 ? vec2(-1., -1.) : gl_VertexID == 1 ? vec2(3., -1.) : vec2(-1., 3.);
    gl_Position = vec4(p, 0., 1.);
}`;
const FRAGMENT = `#version 300 es
precision highp float;
precision highp int;
uniform sampler2D panorama;
uniform vec2 resolution;
uniform float cameraHeight;
uniform vec4 camera; // longitude, latitude, tan(verticalFOV/2), output aspect
out vec4 color;
const float PI = 3.141592653589793;
vec3 texel(ivec2 p, ivec2 size) {
    p.x = ((p.x % size.x) + size.x) % size.x;
    p.y = clamp(p.y, 0, size.y - 1);
    return texelFetch(panorama, p, 0).rgb;
}
void main() {
    vec2 screen = gl_FragCoord.xy / resolution * 2. - 1.;
    float x = screen.x * camera.z * camera.w;
    float y = screen.y * camera.z;
    float cp = cos(camera.y), sp = sin(camera.y), cy = cos(camera.x), sy = sin(camera.x);
    float py = y * cp + sp;
    float pz = -y * sp + cp;
    float wx = x * cy + pz * sy, wz = -x * sy + pz * cy;
    float norm = sqrt(x*x + y*y + 1.);
    if (cameraHeight != 0.) {
        vec3 d = vec3(wx, py, wz) / norm;
        float hd = cameraHeight * d.y;
        float distance = -hd + sqrt(1. - cameraHeight*cameraHeight + hd*hd);
        vec3 p = vec3(0., cameraHeight, 0.) + distance*d;
        wx = p.x; py = p.y; wz = p.z; norm = 1.;
    }
    vec2 uv = vec2(fract(atan(wx, wz) / (2. * PI) + .5),
                   .5 - asin(clamp(py / norm, -1., 1.)) / PI);
    ivec2 size = textureSize(panorama, 0);
    vec2 pixel = uv * vec2(size) - .5;
    ivec2 p = ivec2(floor(pixel));
    vec2 f = fract(pixel);
    vec3 a = mix(texel(p, size), texel(p + ivec2(1, 0), size), f.x);
    vec3 b = mix(texel(p + ivec2(0, 1), size), texel(p + ivec2(1, 1), size), f.x);
    color = vec4(mix(a, b, f.y), 1.);
}`;

export class PanoramaRenderer {
    constructor(canvas) {
        this.canvas = canvas;
        const gl = canvas.getContext('webgl2', {alpha:false,antialias:false,preserveDrawingBuffer:true});
        if (!gl) throw new Error('360 preview requires WebGL2. Enable browser hardware acceleration.');
        this.gl = gl;
        const compile = (type, text) => {
            const shader = gl.createShader(type); gl.shaderSource(shader, text); gl.compileShader(shader);
            if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
                const error = gl.getShaderInfoLog(shader); gl.deleteShader(shader); throw new Error(error);
            }
            return shader;
        };
        const vertex = compile(gl.VERTEX_SHADER, VERTEX);
        let fragment;
        try { fragment = compile(gl.FRAGMENT_SHADER, FRAGMENT); }
        catch (error) { gl.deleteShader(vertex); throw error; }
        const program = gl.createProgram();
        gl.attachShader(program, vertex); gl.attachShader(program, fragment); gl.linkProgram(program);
        gl.deleteShader(vertex); gl.deleteShader(fragment);
        if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
            const error = gl.getProgramInfoLog(program); gl.deleteProgram(program); throw new Error(error);
        }
        this.program = program;
        this.cameraUniform = gl.getUniformLocation(program, 'camera');
        this.resolutionUniform = gl.getUniformLocation(program, 'resolution');
        this.heightUniform = gl.getUniformLocation(program, 'cameraHeight');
        this.texture = gl.createTexture(); this.vao = gl.createVertexArray();
        gl.bindVertexArray(this.vao); gl.bindTexture(gl.TEXTURE_2D, this.texture);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
        gl.useProgram(program); gl.uniform1i(gl.getUniformLocation(program, 'panorama'), 0);
    }

    upload(image) {
        const gl = this.gl;
        gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, this.texture);
        gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, false);
        gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL, false);
        gl.pixelStorei(gl.UNPACK_COLORSPACE_CONVERSION_WEBGL, gl.NONE);
        gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, image);
    }

    render({cx, cy, zoom, aspect, cameraHeight = 0}, width, height) {
        const gl = this.gl;
        if (this.canvas.width !== width) this.canvas.width = width;
        if (this.canvas.height !== height) this.canvas.height = height;
        const {yaw, pitch, tangent} = cameraAngles(cx, cy, zoom);
        gl.viewport(0, 0, width, height); gl.useProgram(this.program); gl.bindVertexArray(this.vao);
        gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, this.texture);
        gl.uniform2f(this.resolutionUniform, width, height);
        gl.uniform4f(this.cameraUniform, yaw, pitch, tangent, aspect);
        gl.uniform1f(this.heightUniform, cameraHeight);
        gl.drawArrays(gl.TRIANGLES, 0, 3);
    }

    destroy() {
        const gl = this.gl;
        gl.deleteTexture(this.texture); gl.deleteProgram(this.program); gl.deleteVertexArray(this.vao);
    }
}
