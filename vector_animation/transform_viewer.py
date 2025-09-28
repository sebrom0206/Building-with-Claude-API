import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, TextBox


# ---------- helpers ----------
def draw_grid(ax, n=10, lim=3, color="#cccccc"):
    xs = np.linspace(-lim, lim, 2 * n + 1)
    for x in xs:
        ax.plot([x, x], [-lim, lim], color=color, lw=0.6, zorder=0)
        ax.plot([-lim, lim], [x, x], color=color, lw=0.6, zorder=0)


def transform_points(A, P):
    return (A @ P.T).T


def arrow(ax, p, q, **kw):
    ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle="->", lw=2, **kw))


def unit_square():
    return np.array([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]], dtype=float)


# ---------- initial state ----------
A = np.array([[1.0, 0.0], [0.0, 1.0]])  # identity
v = np.array([1.0, 1.0])

# ---------- figure layout ----------
plt.close("all")
fig = plt.figure(figsize=(11, 6))
gs = fig.add_gridspec(2, 2, height_ratios=[20, 1], width_ratios=[1, 1], hspace=0.15)

ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])
ax1.set_title("Original space")
ax2.set_title("Transformed space")

for ax in (ax1, ax2):
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(-3, 3)
    ax.set_ylim(-3, 3)
    draw_grid(ax)

# info text
info = ax2.text(0.02, 0.98, "", transform=ax2.transAxes, va="top", ha="left")

# sliders / inputs area
ax_a = fig.add_subplot(gs[1, 0])
ax_b = ax_a.inset_axes([0.02, 0.55, 0.96, 0.35])
ax_c = ax_a.inset_axes([0.02, 0.10, 0.96, 0.35])
ax_d = fig.add_subplot(gs[1, 1]).inset_axes([0.02, 0.55, 0.96, 0.35])

# vector input boxes
box_vec = fig.add_subplot(gs[1, 1]).inset_axes([0.02, 0.05, 0.46, 0.35])
box_lab = fig.add_subplot(gs[1, 1]).inset_axes([0.52, 0.05, 0.46, 0.35])

sa = Slider(ax_b, "a (row1 col1)", -3.0, 3.0, valinit=A[0, 0])
sb = Slider(ax_c, "b (row1 col2)", -3.0, 3.0, valinit=A[0, 1])
sd = Slider(ax_d, "d (row2 col2)", -3.0, 3.0, valinit=A[1, 1])

# We'll infer c from a separate mini slider to keep UI compact
ax_c2 = ax2.inset_axes([0.65, 0.01, 0.32, 0.05])
sc = Slider(ax_c2, "c (row2 col1)", -3.0, 3.0, valinit=A[1, 0])

tbox_vec = TextBox(box_vec, "Vector v = [x, y]", initial="1, 1")
tbox_lab = TextBox(box_lab, "Label", initial="v")

# ---------- artists (persistent) ----------
# Original basis & vector
e1, e2 = np.array([1, 0]), np.array([0, 1])
orig_basis1 = ax1.plot([0, e1[0]], [0, e1[1]], lw=2, color="#1f77b4", label="e1")[0]
orig_basis2 = ax1.plot([0, e2[0]], [0, e2[1]], lw=2, color="#ff7f0e", label="e2")[0]
orig_vec = ax1.plot([0, v[0]], [0, v[1]], lw=2, color="#2ca02c", label="v")[0]
orig_square = ax1.plot(*unit_square().T, color="#9467bd", lw=1.8, label="unit square")[
    0
]

# Transformed
(tr_basis1,) = ax2.plot([], [], lw=2, color="#1f77b4", label="A e1")
(tr_basis2,) = ax2.plot([], [], lw=2, color="#ff7f0e", label="A e2")
(tr_vec,) = ax2.plot([], [], lw=2, color="#2ca02c", label="A v")
(tr_square,) = ax2.plot([], [], color="#9467bd", lw=1.8, label="A·(unit square)")

ax1.legend(loc="upper left")
ax2.legend(loc="upper left")


# ---------- update routine ----------
def parse_vec(text):
    try:
        parts = text.replace("[", "").replace("]", "").split(",")
        x = float(parts[0])
        y = float(parts[1])
        return np.array([x, y], dtype=float)
    except Exception:
        return np.array([1.0, 1.0])


def update(_=None):
    A[0, 0] = sa.val
    A[0, 1] = sb.val
    A[1, 0] = sc.val
    A[1, 1] = sd.val

    vec = parse_vec(tbox_vec.text)

    # original plot refresh
    orig_basis1.set_data([0, 1], [0, 0])
    orig_basis2.set_data([0, 0], [0, 1])
    orig_vec.set_data([0, vec[0]], [0, vec[1]])
    orig_square.set_data(*unit_square().T)

    # transformed basis, vector, unit square
    Ae1 = A @ e1
    Ae2 = A @ e2
    Av = A @ vec
    sqT = transform_points(A, unit_square())

    tr_basis1.set_data([0, Ae1[0]], [0, Ae1[1]])
    tr_basis2.set_data([0, Ae2[0]], [0, Ae2[1]])
    tr_vec.set_data([0, Av[0]], [0, Av[1]])
    tr_square.set_data(sqT[:, 0], sqT[:, 1])

    det = np.linalg.det(A)
    orientation = "reverses orientation" if det < 0 else "preserves orientation"
    info.set_text(
        f"A = [[{A[0,0]:.2f}, {A[0,1]:.2f}], [{A[1,0]:.2f}, {A[1,1]:.2f}]]\n"
        f"det(A) = {det:.3f}  →  {orientation}\n"
        f"‖Av‖ = {np.linalg.norm(Av):.3f}"
    )

    fig.canvas.draw_idle()


# connect events
for slider in (sa, sb, sc, sd):
    slider.on_changed(update)
tbox_vec.on_submit(lambda _: update())
tbox_lab.on_submit(
    lambda s: tr_vec.set_label(s) or ax2.legend() or fig.canvas.draw_idle()
)

update()
plt.show()
