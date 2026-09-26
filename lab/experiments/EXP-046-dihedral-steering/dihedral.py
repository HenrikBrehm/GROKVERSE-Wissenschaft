"""EXP-046: dihedral group D_n (order 2n, n odd) - elements, composition, real irreps, W_E irrep power, mask power.

Element index i: i < n -> rotation r^i; i >= n -> reflection s r^(i-n). Written s^f r^m.
Composition (r s = s r^-1):  (s^f1 r^m1)(s^f2 r^m2) = s^(f1+f2) r^((-1)^f2 m1 + m2).
Irreps for odd n: trivial, sign (s -> -1), and (n-1)/2 two-dimensional rho_k(s^f r^m) = S^f R(2 pi k m / n),
k = 1..(n-1)/2, S = diag(1, -1). Pure numpy; the self checks run inside every public entry point.
"""
from __future__ import annotations

import numpy as np


def parts(n: int) -> tuple[np.ndarray, np.ndarray]:
    i = np.arange(2 * n)
    return (i >= n).astype(int), i % n                     # f, m


def compose_table(n: int) -> np.ndarray:
    """table[a, b] = index of a*b."""
    f, m = parts(n)
    f1, m1, f2, m2 = f[:, None], m[:, None], f[None, :], m[None, :]
    fc = (f1 + f2) % 2
    mc = (np.where(f2 == 1, -m1, m1) + m2) % n
    return fc * n + mc


def rho(n: int, k: int) -> np.ndarray:
    """(2n, 2, 2) matrices of the 2-dim irrep k."""
    f, m = parts(n)
    th = 2 * np.pi * k * m / n
    R = np.stack([np.stack([np.cos(th), -np.sin(th)], -1), np.stack([np.sin(th), np.cos(th)], -1)], -2)
    S = np.where(f[:, None, None] == 1, np.diag([1.0, -1.0])[None], np.eye(2)[None])
    return S @ R


def n_irrep2(n: int) -> int:
    return (n - 1) // 2


def check_group(n: int) -> None:
    """Fail closed: odd n, table is a non-abelian group law, every rho_k is a homomorphism, basis orthonormal."""
    if n < 3 or n % 2 == 0:
        raise SystemExit(f"D_n needs odd n >= 3, got {n}")
    T = compose_table(n)
    G = 2 * n
    if not all(sorted(T[a].tolist()) == list(range(G)) for a in range(G)):
        raise SystemExit("composition table is not a Latin square")
    if np.array_equal(T, T.T):
        raise SystemExit("composition table is abelian")
    if not np.array_equal(T[T[:, :, None], np.arange(G)[None, None, :]],      # (ab)c
                          T[np.arange(G)[:, None, None], T[None, :, :]]):      # a(bc)
        raise SystemExit("composition is not associative")
    for k in range(1, n_irrep2(n) + 1):
        r = rho(n, k)
        if not np.allclose(r[:, None] @ r[None, :], r[T]):
            raise SystemExit(f"rho_{k} is not a homomorphism")
    B = irrep_basis(n, check=False)[0]
    if not np.allclose(B.T @ B, np.eye(G), atol=1e-9):
        raise SystemExit("irrep basis is not orthonormal")


def irrep_basis(n: int, check: bool = True) -> tuple[np.ndarray, list[str]]:
    """Orthonormal (2n x 2n) basis of functions on D_n, columns grouped by irrep; labels per column."""
    if check:
        check_group(n)
    f, _ = parts(n)
    G = 2 * n
    cols, labels = [np.ones(G), np.where(f == 1, -1.0, 1.0)], ["triv", "sign"]
    for k in range(1, n_irrep2(n) + 1):
        r = rho(n, k)
        for i in range(2):
            for j in range(2):
                cols.append(r[:, i, j])
                labels.append(f"k{k}")
    B = np.stack(cols, 1)
    return B / np.linalg.norm(B, axis=0, keepdims=True), labels


def irrep_power(W: np.ndarray, B: np.ndarray, labels: list[str], n: int) -> np.ndarray:
    """Power of W (2n x d) in each 2-dim irrep k = 1..(n-1)/2 (index k-1); trivial and sign excluded."""
    C = B.T @ W
    lab = np.array(labels)
    return np.array([float((C[lab == f"k{k}"] ** 2).sum()) for k in range(1, n_irrep2(n) + 1)])


def mask_power(idx: np.ndarray, n: int) -> np.ndarray:
    """Non-abelian EXP-015 M0: for every output c, left N_L(t) = [(t, t^-1 c) in train], right N_R(t) = [(c t^-1, t)
    in train]; power of irrep k = d * ||sum_t N(t) rho_k(t)||_F^2 summed over c and both sides (d = 2)."""
    check_group(n)
    G = 2 * n
    T = compose_table(n)
    Mk = np.zeros((G, G))
    Mk[idx // G, idx % G] = 1.0
    inv = np.argmax(T == 0, axis=1)                        # inv[t] = t^-1 (identity has index 0)
    t, c = np.arange(G)[:, None], np.arange(G)[None, :]
    left = Mk[t, T[inv[t], c]]                             # (t, c): pair (t, t^-1 c)
    right = Mk[T[c, inv[t]], t]                            # (t, c): pair (c t^-1, t)
    out = []
    for k in range(1, n_irrep2(n) + 1):
        r = rho(n, k).reshape(G, 4)
        out.append(2.0 * float(((left.T @ r) ** 2).sum() + ((right.T @ r) ** 2).sum()))
    return np.array(out)
