import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, TextBox
from mpl_toolkits.mplot3d.art3d import Line3DCollection


# ------------- helpers -------------
def make_plane(axis="xy", lim=1.5, n=9):
    s = np.linspace(-lim, lim, n)
    if axis == "xy":
        X, Y = np.meshgrid(s, s)
        Z = np.zeros_like(X)
    elif axis == "xz":
        X, Z = np.meshgrid(s, s)
        Y = np.zeros_like(X)
    else:  # yz
        Y, Z = np.meshgrid(s, s)
        X = np.zeros_like(Y)
    P = np.stack([X, Y, Z], axis=-1).reshape(-1, 3)
    return P, X.shape


def transform_points(A, P):
    return (A @ P.T).T


def unit_cube_edges():
    # 12 edges of the cube [0,1]^3
    pts = np.array(
        [
            [0, 0, 0],
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1],
            [1, 1, 0],
            [1, 0, 1],
            [0, 1, 1],
            [1, 1, 1],
        ],
        float,
    )
    edges = [
        (0, 1),
        (0, 2),
        (0, 3),
        (1, 4),
        (1, 5),
        (2, 4),
        (2, 6),
        (3, 5),
        (3, 6),
        (4, 7),
        (5, 7),
        (6, 7),
    ]
    return pts, edges


def to_segments(P, edges):
    return [np.vstack([P[i], P[j]]) for (i, j) in edges]


def set_axes_equal(ax, margin=0.05):
    # Make 3D axes have equal scale on all axes
    xlim = np.array(ax.get_xlim3d())  # [xmin, xmax]
    ylim = np.array(ax.get_ylim3d())
    zlim = np.array(ax.get_zlim3d())

    xyz = np.vstack([xlim, ylim, zlim])  # shape (3, 2)
    span = xyz[:, 1] - xyz[:, 0]
    maxspan = span.max()
    mid = xyz.mean(axis=1)  # shape (3,)

    # Build per-axis [min, max] pairs -> shape (3, 2)
    new = np.vstack(
        [
            mid - 0.5 * maxspan * (1 + margin),
            mid + 0.5 * maxspan * (1 + margin),
        ]
    ).T

    ax.set_xlim(new[0, 0], new[0, 1])
    ax.set_ylim(new[1, 0], new[1, 1])
    ax.set_zlim(new[2, 0], new[2, 1])


# ------------- initial state -------------
A = np.eye(3)
v = np.array([1.0, 1.0, 0.5])

# plane point clouds
P_xy, shape_xy = make_plane("xy", lim=1.2, n=11)
P_xz, shape_xz = make_plane("xz", lim=1.2, n=11)
P_yz, shape_yz = make_plane("yz", lim=1.2, n=11)

# unit cube
C_pts, C_edges = unit_cube_edges()

# ------------- figure layout -------------
plt.close("all")
fig = plt.figure(figsize=(13, 7))
gs = fig.add_gridspec(
    2, 2, height_ratios=[20, 1], width_ratios=[1, 1], wspace=0.1, hspace=0.2
)
ax1 = fig.add_subplot(gs[0, 0], projection="3d")
ax2 = fig.add_subplot(gs[0, 1], projection="3d")

ax1.set_title("Original space")
ax2.set_title("Transformed space  (by A)")

for ax in (ax1, ax2):
    ax.set_box_aspect([1, 1, 1])
    ax.set_xlim(-1.8, 1.8)
    ax.set_ylim(-1.8, 1.8)
    ax.set_zlim(-1.8, 1.8)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
set_axes_equal(ax1)
set_axes_equal(ax2)

# info text
info = ax2.text2D(
    0.02, 0.98, "", transform=ax2.transAxes, va="top", ha="left", fontsize=10
)

# ------------- artists (persistent) -------------

# Original basis arrows
e1, e2, e3 = np.eye(3)
orig_e1 = ax1.quiver(0, 0, 0, *e1, color="#1f77b4", linewidth=2)
orig_e2 = ax1.quiver(0, 0, 0, *e2, color="#ff7f0e", linewidth=2)
orig_e3 = ax1.quiver(0, 0, 0, *e3, color="#2ca02c", linewidth=2)

# Original vector v
orig_v = ax1.quiver(0, 0, 0, *v, color="#9467bd", linewidth=2)


# Original planes (wire grids)
def plane_wire(ax, P, shape, color):
    X = P[:, 0].reshape(shape)
    Y = P[:, 1].reshape(shape)
    Z = P[:, 2].reshape(shape)
    # draw row and column lines as light wireframe
    rows = [np.vstack([X[i, :], Y[i, :], Z[i, :]]).T for i in range(shape[0])]
    cols = [np.vstack([X[:, j], Y[:, j], Z[:, j]]).T for j in range(shape[1])]
    segs = rows + cols
    coll = Line3DCollection(segs, colors=color, linewidths=0.6, alpha=0.7)
    ax.add_collection3d(coll)
    return coll


wire_xy = plane_wire(ax1, P_xy, shape_xy, "#cccccc")
wire_xz = plane_wire(ax1, P_xz, shape_xz, "#cccccc")
wire_yz = plane_wire(ax1, P_yz, shape_yz, "#cccccc")

# Original unit cube wire
cube_orig_segments = to_segments(C_pts, C_edges)
cube_orig = Line3DCollection(
    cube_orig_segments, colors="#7f7f7f", linewidths=1.2, alpha=0.9
)
ax1.add_collection3d(cube_orig)

# Transformed basis & vector
tr_e1 = ax2.quiver(0, 0, 0, 0, 0, 0, color="#1f77b4", linewidth=2)
tr_e2 = ax2.quiver(0, 0, 0, 0, 0, 0, color="#ff7f0e", linewidth=2)
tr_e3 = ax2.quiver(0, 0, 0, 0, 0, 0, color="#2ca02c", linewidth=2)
tr_v = ax2.quiver(0, 0, 0, 0, 0, 0, color="#9467bd", linewidth=2)

# Transformed planes (wire grids)
wire_xy_t = plane_wire(ax2, P_xy, shape_xy, "#a0c4ff")
wire_xz_t = plane_wire(ax2, P_xz, shape_xz, "#caffbf")
wire_yz_t = plane_wire(ax2, P_yz, shape_yz, "#ffd6a5")

# Transformed unit cube
cube_tr = Line3DCollection([], colors="#444", linewidths=1.4)
ax2.add_collection3d(cube_tr)

# legends
ax1.legend(
    [orig_e1, orig_e2, orig_e3, orig_v], ["e1", "e2", "e3", "v"], loc="upper left"
)
ax2.legend(
    [tr_e1, tr_e2, tr_e3, tr_v], ["A·e1", "A·e2", "A·e3", "A·v"], loc="upper left"
)

# ------------- sliders / inputs -------------
# matrix sliders a11..a33 and vector v
slab = fig.add_axes([0.10, 0.08, 0.80, 0.03])  # a11..a13
slcd = fig.add_axes([0.10, 0.04, 0.80, 0.03])  # a21..a23
slfg = fig.add_axes([0.10, 0.00, 0.80, 0.03])  # a31..a33

sa11 = Slider(slab, "a11 a12 a13", -3, 3, valinit=A[0, 0])
sa12 = Slider(fig.add_axes([0.10, 0.12, 0.24, 0.03]), "", -3, 3, valinit=A[0, 1])
sa13 = Slider(fig.add_axes([0.38, 0.12, 0.24, 0.03]), "", -3, 3, valinit=A[0, 2])

sa21 = Slider(slcd, "a21 a22 a23", -3, 3, valinit=A[1, 0])
sa22 = Slider(fig.add_axes([0.10, 0.16, 0.24, 0.03]), "", -3, 3, valinit=A[1, 1])
sa23 = Slider(fig.add_axes([0.38, 0.16, 0.24, 0.03]), "", -3, 3, valinit=A[1, 2])

sa31 = Slider(slfg, "a31 a32 a33", -3, 3, valinit=A[2, 0])
sa32 = Slider(fig.add_axes([0.10, 0.20, 0.24, 0.03]), "", -3, 3, valinit=A[2, 1])
sa33 = Slider(fig.add_axes([0.38, 0.20, 0.24, 0.03]), "", -3, 3, valinit=A[2, 2])

# vector TextBox
ax_vec = fig.add_axes([0.66, 0.16, 0.28, 0.055])
tbox_vec = TextBox(ax_vec, "v = [vx, vy, vz]", initial="1, 1, 0.5")


# ------------- update routine -------------
def parse_vec(s):
    try:
        parts = s.replace("[", "").replace("]", "").split(",")
        vx, vy, vz = [float(x) for x in parts[:3]]
        return np.array([vx, vy, vz], float)
    except Exception:
        return np.array([1.0, 1.0, 0.5])


def refresh_plane_wire(coll, P, shape, A):
    T = transform_points(A, P)
    X = T[:, 0].reshape(shape)
    Y = T[:, 1].reshape(shape)
    Z = T[:, 2].reshape(shape)
    rows = [np.vstack([X[i, :], Y[i, :], Z[i, :]]).T for i in range(shape[0])]
    cols = [np.vstack([X[:, j], Y[:, j], Z[:, j]]).T for j in range(shape[1])]
    coll.set_segments(rows + cols)


def refresh_cube(coll, A):
    T = transform_points(A, C_pts)
    segs = to_segments(T, C_edges)
    coll.set_segments(segs)


def update(_=None):
    # matrix from sliders
    A[0, 0] = sa11.val
    A[0, 1] = sa12.val
    A[0, 2] = sa13.val
    A[1, 0] = sa21.val
    A[1, 1] = sa22.val
    A[1, 2] = sa23.val
    A[2, 0] = sa31.val
    A[2, 1] = sa32.val
    A[2, 2] = sa33.val

    vec = parse_vec(tbox_vec.text)
    Av = A @ vec

    # transformed basis
    Ae1 = A @ e1
    Ae2 = A @ e2
    Ae3 = A @ e3
    for q, u in [(tr_e1, Ae1), (tr_e2, Ae2), (tr_e3, Ae3), (tr_v, Av)]:
        # update 3D quiver by removing and re-adding (quiver has limited setters)
        q.remove()
    tr_e1 = ax2.quiver(0, 0, 0, *Ae1, color="#1f77b4", linewidth=2)
    tr_e2 = ax2.quiver(0, 0, 0, *Ae2, color="#ff7f0e", linewidth=2)
    tr_e3 = ax2.quiver(0, 0, 0, *Ae3, color="#2ca02c", linewidth=2)
    tr_v = ax2.quiver(0, 0, 0, *Av, color="#9467bd", linewidth=2)

    # refresh planes & cube
    refresh_plane_wire(wire_xy_t, P_xy, shape_xy, A)
    refresh_plane_wire(wire_xz_t, P_xz, shape_xz, A)
    refresh_plane_wire(wire_yz_t, P_yz, shape_yz, A)
    refresh_cube(cube_tr, A)

    # info
    det = np.linalg.det(A)
    info.set_text(
        "A =\n"
        f"[{A[0,0]:6.2f} {A[0,1]:6.2f} {A[0,2]:6.2f}]\n"
        f"[{A[1,0]:6.2f} {A[1,1]:6.2f} {A[1,2]:6.2f}]\n"
        f"[{A[2,0]:6.2f} {A[2,1]:6.2f} {A[2,2]:6.2f}]\n"
        f"det(A) = {det:.3f}  ({'orientation flip' if det < 0 else 'preserves orientation'})\n"
        f"||A·v|| = {np.linalg.norm(Av):.3f}"
    )

    # rebind updated quivers into outer scope (Python trick)
    update.tr_e1, update.tr_e2, update.tr_e3, update.tr_v = tr_e1, tr_e2, tr_e3, tr_v
    fig.canvas.draw_idle()


# keep references for updated quivers
update.tr_e1, update.tr_e2, update.tr_e3, update.tr_v = tr_e1, tr_e2, tr_e3, tr_v

# connect
for sld in (sa11, sa12, sa13, sa21, sa22, sa23, sa31, sa32, sa33):
    sld.on_changed(update)
tbox_vec.on_submit(lambda _: update())

# initial draw
update()
plt.show()
