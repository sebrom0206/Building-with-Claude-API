import math
import sys
import time

# Terminal resolution
W = 80
H = 40

# Camera distance and projection scale
K2 = 5.0
K1 = 30.0

# Angular velocities
DTX = 0.02
DTY = 0.035
DTZ = 0.017

SHADE = ".,-~:;=!*#$@"
LIGHT_DIR = (0.1, 1.0, -1.0)

# Geometry
V = [(x, y, z) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
F = [
    (0, 1, 3),
    (0, 3, 2),
    (4, 6, 7),
    (4, 7, 5),
    (0, 4, 5),
    (0, 5, 1),
    (2, 3, 7),
    (2, 7, 6),
    (0, 2, 6),
    (0, 6, 4),
    (1, 5, 7),
    (1, 7, 3),
]


# Math helpers
def rot_matrix(ax, ay, az):
    cx = math.cos(ax)
    sx = math.sin(ax)
    cy = math.cos(ay)
    sy = math.sin(ay)
    cz = math.cos(az)
    sz = math.sin(az)
    Rx = ((1, 0, 0), (0, cx - sx), (0, sx, cx))
    Ry = ((cy, 0, sy), (0, 1, 0), (-sy, 0, cy))
    Rz = ((cz, -sz, 0), (sz, cz, 0), (0, 0, 1))

    def mm(A, B):
        return tuple(
            tuple(sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3))
            for i in range(3)
        )

    return mm(mm(Rz, Ry), Rx)


def apply_R(v, R):
    x, y, z = v
    return (
        R[0][0] * x + R[0][1] * y + R[0][2] * z,
        R[1][0] * x + R[1][1] * y + R[1][2] * z,
        R[2][0] * x + R[2][1] * y + R[2][2] * z,
    )


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def norm(a):
    m = math.sqrt(dot(a, a))
    return (a[0] / m, a[1] / m, a[2] / m) if m > 0 else (0, 0, 0)


def project(p):
    x, y, z = p
    zc = z + K2
    if zc <= 1e-6:
        zc = 1e-6
    ooz = 1.0 / zc
    xp = int(W / 2 + K1 * x * ooz)
    yp = int(H / 2 + K1 * y * ooz)
    return xp, yp, ooz


def clear_buffers():
    return [[" "] * W for _ in range(H)], [[0.0] * W for _ in range(H)]


def put(output, zbuf, x, y, ooz, ch):
    if 0 <= x < W and 0 <= y < H and ooz > zbuf[y][x]:
        zbuf[y][x] = ooz
        output[y][x] = ch


def shade_from_luminance(L):
    if L < 0:
        L = 0.0
    if L > 1:
        L = 1.0
    idx = int(L * (len(SHADE) - 1) + 1e-6)
    return SHADE[idx]


# Barycentric helpers
def edge(x0, y0, x1, y1, px, py):
    return (px - x0) * (y1 - y0) - (py - y0) * (x1 - x0)


def rasterize_triangle(output, zbuf, P, chars, oozs):
    # P: [(x0,y0),(x1,y1),(x2,y2)] in screen space
    # oozs: [ooz0, ooz1, ooz2]
    (x0, y0), (x1, y1), (x2, y2) = P
    o0, o1, o2 = oozs

    minx = max(min(x0, x1, x2), 0)
    maxx = min(max(x0, x1, x2), W - 1)
    miny = max(min(y0, y1, y2), 0)
    maxy = min(max(y0, y1, y2), H - 1)
    if minx > maxx or miny > maxy:
        return

    # area (double)
    area = edge(x0, y0, x1, y1, x2, y2)
    if area == 0:
        return

    for y in range(miny, maxy + 1):
        for x in range(minx, maxx + 1):
            w0 = edge(x1, y1, x2, y2, x, y)
            w1 = edge(x2, y2, x0, y0, x, y)
            w2 = edge(x0, y0, x1, y1, x, y)
            # same sign as area (top-left rule could be added for perfect coverage)
            if (w0 >= 0 and w1 >= 0 and w2 >= 0) or (w0 <= 0 and w1 <= 0 and w2 <= 0):
                # barycentric normalized
                w0n = w0 / area
                w1n = w1 / area
                w2n = w2 / area
                ooz = w0n * o0 + w1n * o1 + w2n * o2
                put(output, zbuf, x, y, ooz, chars)


def main():
    sys.stdout.write("\x1b[2J")  # clear once
    ax = ay = az = 0.0
    L = norm(LIGHT_DIR)

    while True:
        R = rot_matrix(ax, ay, az)

        # Transform to camera space (rotate only; translation is via +K2 on z in project)
        Vc = [apply_R(v, R) for v in V]

        output, zbuf = clear_buffers()

        # Render each triangle
        for i0, i1, i2 in F:
            A = Vc[i0]
            B = Vc[i1]
            C = Vc[i2]

            # Backface culling via camera-space normal
            n = cross(sub(B, A), sub(C, A))  # not normalized yet
            # View dir from camera to triangle is roughly +z in our convention;
            # But we want to keep triangles with normal.z < 0 (pointing towards camera)
            if n[2] >= 0:  # culled (flip sign based on your winding if needed)
                continue

            # Flat-shaded luminance
            n_unit = norm(n)
            lum = dot(n_unit, L)
            if lum <= 0:
                continue
            ch = shade_from_luminance(lum)

            # Project
            Ax, Ay, ao = project(A)
            Bx, By, bo = project(B)
            Cx, Cy, co = project(C)

            rasterize_triangle(
                output, zbuf, [(Ax, Ay), (Bx, By), (Cx, Cy)], ch, [ao, bo, co]
            )

        # print the frame
        sys.stdout.write("\x1b[H")
        for row in output:
            sys.stdout.write("".join(row) + "\n")
        sys.stdout.flush()

        ax += DTX
        ay += DTY
        az += DTZ
        time.sleep(0.03)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
